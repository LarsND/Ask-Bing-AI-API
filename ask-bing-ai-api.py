import asyncio
import json
import random
import uuid
from typing import List, Generator, Optional
import tls_client
import websockets.client as websockets
from flask import Flask, request

debug_app = False

command_psk = "notthebestwaytodothis"

delimiter = "\x1e"

forwarded_ip = (f"13.{random.randint(104, 107)}.{random.randint(0, 255)}.{random.randint(0, 255)}") # Generate random IP between range 13.104.0.0/14

headers = {
    "accept": "application/json",
    "accept-language": "nl-NL,nl;q=0.9",
    "content-type": "application/json",
    "sec-ch-ua": '"Not_A Brand";v="99", "Microsoft Edge";v="109", "Chromium";v="109"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"109.0.1518.78"',
    "sec-ch-ua-full-version-list": '"Not_A Brand";v="99.0.0.0", "Microsoft Edge";v="109.0.1518.78", "Chromium";v="109.0.5414.120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-ms-client-request-id": str(uuid.uuid4()),
    "x-ms-useragent": "azsdk-js-api-client-factory/1.0.0-beta.1 core-rest-pipeline/1.10.0 OS/Win32",
    "Referer": "https://www.bing.com/search?q=Bing+AI&showconv=1&FORM=hpcodx",
    "Referrer-Policy": "origin-when-cross-origin",
    "x-forwarded-for": forwarded_ip,
}

def append_identifier(msg: dict) -> str:
    # Convert dict to json string
    return json.dumps(msg) + delimiter

class ChatHubRequest:
    def __init__(self, conversation_signature: str, client_id: str, conversation_id: str, invocation_id: int = 0) -> None:
        self.struct: dict = {}
        self.client_id: str = client_id
        self.conversation_id: str = conversation_id
        self.conversation_signature: str = conversation_signature
        self.invocation_id: int = invocation_id

    def update(self, prompt: str, options: list = None) -> None:
        if options is None:
            options = [
                "deepleo",
                "enable_debug_commands",
                "disable_emoji_spoken_text",
                "enablemm",
            ]
        self.struct = {
            "arguments": [
                {
                    "source": "cib",
                    "optionsSets": options,
                    "isStartOfSession": self.invocation_id == 0,
                    "message": {
                        "author": "user",
                        "inputMethod": "Keyboard",
                        "text": prompt,
                        "messageType": "Chat",
                    },
                    "conversationSignature": self.conversation_signature,
                    "participant": {
                        "id": self.client_id,
                    },
                    "conversationId": self.conversation_id,
                },
            ],
            "invocationId": str(self.invocation_id),
            "target": "chat",
            "type": 4,
        }
        self.invocation_id += 1

class Conversation:
    def __init__(self) -> None:
        self.struct: dict = {
            "conversationId": None,
            "clientId": None,
            "conversationSignature": None,
            "result": {"value": "Success", "message": None},
        }
        self.session = tls_client.Session(client_identifier="chrome_108")
        with open('cookie.txt', 'r') as f:
            cookie = f.read()
        self.session.cookies.set("_U", cookie)

        url = "https://edgeservices.bing.com/edgesvc/turing/conversation/create"
        # Send GET request
        response = self.session.get(url, timeout_seconds=30, headers=headers, allow_redirects=True)
        if response.status_code != 200:
            print(f"Status code: {response.status_code}")
            print(response.text)

        self.struct = response.json()

class ChatHub:
    def __init__(self) -> None:
        self.wss: Optional[websockets.WebSocketClientProtocol] = None
        self.request: ChatHubRequest
        self.loop: bool
        self.task: asyncio.Task

        conversation = Conversation()

        try:
            self.request = ChatHubRequest(conversation_signature=conversation.struct["conversationSignature"], client_id=conversation.struct["clientId"], conversation_id=conversation.struct["conversationId"])
        except:
            print("Request for chathub failed!")

    async def ask_stream(self, prompt: str) -> Generator[str, None, None]:
        # Check if websocket is closed
        if self.wss and self.wss.closed or not self.wss:
            self.wss = await websockets.connect("wss://sydney.bing.com/sydney/ChatHub", extra_headers=headers, max_size=None)
            await self.__initial_handshake()
        # Construct a ChatHub request
        self.request.update(prompt=prompt)
        # Send request
        await self.wss.send(append_identifier(self.request.struct))
        final = False
        while not final:
            objects = str(await self.wss.recv()).split(delimiter)
            for obj in objects:
                if obj is None or obj == "":
                    continue
                response = json.loads(obj)
                if response.get("type") == 1:
                    yield False, response["arguments"][0]["messages"][0][
                        "adaptiveCards"
                    ][0]["body"][0]["text"]
                elif response.get("type") == 2:
                    final = True
                    yield True, response

    async def __initial_handshake(self):
        await self.wss.send(append_identifier({"protocol": "json", "version": 1}))
        await self.wss.recv()

    def is_alive(self):
        if self.wss and not self.wss.closed:
            return True
        else:
            return False

    async def close(self):
        if self.is_alive():
            await self.wss.close()

class Chatbot:
    def __init__(self) -> None:
        try:
            self.chat_hub: ChatHub = ChatHub()
        except Exception as e:
            print(f"Initialization of chatbot failed! \nThe error is: {e}")

    async def ask(self, prompt: str) -> dict:
        async for final, response in self.chat_hub.ask_stream(prompt=prompt):
            if final:
                return response
        self.chat_hub.wss.close()

    async def ask_stream(self, prompt: str) -> Generator[str, None, None]:
        async for response in self.chat_hub.ask_stream(prompt=prompt):
            yield response

    async def close(self):
        await self.chat_hub.close()

    async def start(self):
        if not self.chat_hub.is_alive():
            self.chat_hub = ChatHub()

    async def reset(self):
        await self.close()
        self.chat_hub = ChatHub()

    async def handle_request(self, prompt: str, filtered: bool = False):
        print("Received request.")
        if debug_app:
            print(f"request: {prompt}")
        bot = Chatbot()
        response = await bot.ask(prompt=prompt)
        print("Sending response.")
        if debug_app:
            print(f"response: {response}")
        if filtered:
            return response["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
        else:
            return response

app = Flask(__name__)
bot = Chatbot()

@app.route("/", methods=["POST"])
def handle_post_raw():
    prompt = request.json.get("prompt")
    filtered = bool(int(request.json.get("filtered")))
    response = asyncio.run(bot.handle_request(prompt, filtered=filtered))
    return {"response": response}

@app.route("/cmd/", methods=["POST"])
def cmd():
    command = str(request.json.get("command"))
    psk = str(request.json.get("psk"))
    if psk == command_psk:
        if command == "reset":
            asyncio.run(bot.reset())
        elif command == "close":
            asyncio.run(bot.close())
        elif command == "start":
            asyncio.run(bot.start())
        else:
            return {"cmd": "command not found. Make sure the command is sent via {`command`: `<your command>`}. Available commands: reset, close, start"}
        return {"cmd": f"executed command {command}"}
    else:
        return {"response": "unauthorized"}

@app.errorhandler(Exception)
def handle_error(error):
    print(f"Error: {error}")
    return {"response": f"An error occurred. Error: {str(error)}"}, 500

if __name__ == "__main__":
    app.run()