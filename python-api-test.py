import requests

# Define the URL for the Flask app
url = "http://127.0.0.1:5000/"

# Define the prompt to send to the chatbot
prompt = input("Input question: ")
conversation_id = input("Input conv. id, or enter nothing to create new ID: ")

if prompt == "customcmd":
    url = "http://127.0.0.1:5000/cmd/"
    if conversation_id != '':
        print(f"Conversation id {conversation_id} sent.")
        data = {"command": input("\nEnter your custom command: "), "psk": "notthebestwaytodothis", "conversation_id": conversation_id}
    else:
        data = {"command": input("\nEnter your custom command: "), "psk": "notthebestwaytodothis"}
else:
    if conversation_id != '':
        print(f"Conversation id {conversation_id} sent.")
        data = {"prompt": prompt, "filtered": 1, "conversation_id": conversation_id}
    else:
        data = {"prompt": prompt, "filtered": 1}

# Send the HTTP POST request to the Flask app
response = requests.post(url, json=data)

# Print the response from the chatbot
print(response.text)