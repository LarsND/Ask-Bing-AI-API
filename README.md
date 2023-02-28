# Ask-Bing-AI-API
Unofficial API implementation of Bing AI bot. Exposes API which can be used to interact with Bing (example included).

This repository contains code for interacting with the Bing AI API using Python. It includes a Flask app that serves as an interface to send prompts to the API and get responses from the chatbot. 

## Requirements
- Python 3.7 or higher
- `Flask` library
- `websockets` library
- `tls-client` library
- `requests` library

## Usage

To use this code, first install the required libraries by running:

```python
pip install -r requirements.txt
```

Then, run the Flask app by executing:

```python
python ask-bing-ai-api.py
```

The Flask app listens on http://127.0.0.1:5000/ and expects HTTP POST requests in JSON format with a prompt key that contains the user's input and a filtered key set to 1 or 0. The filtered key controls whether or not the response should be filtered to remove metadata.

The Flask app also includes a /cmd/ endpoint that allows you to execute certain commands on the chatbot. The available commands are reset, close, and start. The reset command resets the chatbot's conversation, the close command closes the chatbot's connection, and the start command starts a new chatbot instance. To execute a command, send an HTTP POST request to the /cmd/ endpoint with a command key and a psk key set to the pre-shared key defined in the ask-bing-ai-api.py file.
