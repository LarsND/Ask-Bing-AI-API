# Ask-Bing-AI-API
Unofficial API implementation of Bing AI bot. Exposes API which can be used to interact with Bing (example included).

This repository contains code for interacting with the Bing AI API using Python. It includes a Flask app that serves as an interface to send prompts to the API and get responses from the chatbot. 

## Requirements
- Python 3.7 or higher
- `Flask` library
- `websockets` library
- `requests` library

## Usage

To use this code, first install the required libraries by running:

```python
pip3 install -r requirements.txt
```

Then, run the Flask app by executing:

```python
python3 ask-bing-ai-api.py
```

The Flask app listens on http://127.0.0.1:5000/.

Once the script is running, users can send POST requests to http://127.0.0.1:5000/ with the following JSON data:

    "prompt": The prompt/question to send to the Bing AI API. This is required.
    "filtered": A boolean flag indicating whether or not to filter the response.
    "conversation_id": A string that identifies a particular conversation. If not provided, a new conversation ID will be generated. This is optional.

Example request:

```json
{
    "prompt": "What is the capital of France?",
    "filtered": 1,
}
```

The Flask app also includes a /cmd/ endpoint that allows you to execute certain commands on the chatbot. The available commands are reset, close. The reset command resets the chatbot's conversation, the close command closes the chatbot's connection. To execute a command, send an HTTP POST request to the /cmd/ endpoint with a command key and a psk key set to the pre-shared key defined in the ask-bing-ai-api.py file.

# Credits

Large portion of code stems from [acheong08/EdgeGPT](https://github.com/acheong08/EdgeGPT).
