import requests

# Define the URL for the Flask app
url = "http://127.0.0.1:5000/"

# Define the prompt to send to the chatbot
prompt = input("Input question: ")

if prompt == "customcmd":
    url = "http://127.0.0.1:5000/cmd/"
    data = {"command": input("\nEnter your custom command: "), "psk": "notthebestwaytodothis"}
else:
    data = {"prompt": prompt, "filtered": 1}

# Send the HTTP POST request to the Flask app
response = requests.post(url, json=data)

# Print the response from the chatbot
print(response.text)