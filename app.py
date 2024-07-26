from flask import Flask, jsonify, request
import random
import threading
import time
import requests
import os

import requests
import json

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

jokes = []

title, personality = "unset", "unset"

def generate_jokes():
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'
    api_key = os.environ.get('GEMINI_API_KEY', 'notakey')


    title = os.environ.get('TITLE', 'unset')
    personality = os.environ.get('PERSONALITY', 'unset')

    if personality != "unset":
        # Headers and data
        headers = {
            'Content-Type': 'application/json',
        }

        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Your personality is: " + personality + ". Provide a list of 20 '|' (pipe) separated jokes tightly in line with the personality. Format: joke1|joke2|joke3|joke4| ..."
                        }
                    ]
                }
            ]
        }

        # Make the POST request
        response = requests.post(f"{url}?key={api_key}", headers=headers, data=json.dumps(data))

        # Check the response
        if response.status_code == 200:
            print("Request successful.")
            data = response.json()
            data = data['candidates'][0]['content']['parts'][0]['text']
            print("Jokes", data.split("|"))
            return data.split("|")

        else:
            print(f"Request failed with status code {response.status_code}")
            print("Response:", response.text)

        return []

jokes = generate_jokes()

# Configuration
POST_ENDPOINT = os.environ.get('POST_ENDPOINT', 'http://192.168.0.100:5050/webhook')

def post_joke_periodically():
    while True:
        if len(jokes) > 0:
            joke = random.choice(jokes)
            try:
                response = requests.post(POST_ENDPOINT, json={'joke': joke})
                if response.status_code == 200:
                    print(f"Successfully posted joke: {joke}")
                else:
                    print(f"Failed to post joke. Status code: {response.status_code}")
            except Exception as e:
                print(f"Exception occurred: {e}")
        else:
            print("No joke found.")

        time.sleep(5)

@app.route('/', methods=['GET'])
def get_joke():
    print("Accessing index")
    title = os.getenv('TITLE', 'Not Set')
    personality = os.getenv('PERSONALITY', 'Not Set')
    joke = random.choice(jokes)
    print(f"Title: {title}, Personality: {personality}")
    print(f"Agent posting joke: {joke}")
    return joke

if __name__ == '__main__':
    # Start the background thread
    threading.Thread(target=post_joke_periodically, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
