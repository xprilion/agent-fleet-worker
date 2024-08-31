from flask import Flask, jsonify, request
import random
import threading
import time
import requests
import os
import traceback
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
                            "text": "Your personality is: " + personality + ". Provide a list of 20 '|' (pipe) separated jokes tightly in line with the personality, only safe for work jokes. Format: joke1|joke2|joke3|joke4| ..."
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
            print("Data: ", data)
            data = data['candidates'][0]['content']['parts'][0]['text']
            print("Jokes", data.split("|"))
            return data.split("|")

        else:
            print(f"Request failed with status code {response.status_code}")
            print("Response:", response.text)

        return []

jokes = generate_jokes()

# Configuration
POST_ENDPOINT = os.environ.get('POST_ENDPOINT', 'https://agent-fleet-ui.web.app/api/webhook')
# POST_ENDPOINT = os.environ.get('POST_ENDPOINT', 'http://localhost:3000/api/webhook')


def post_joke_periodically():
    while True:
        if len(jokes) > 0:
            joke = random.choice(jokes)
            current_time = time.time()
            try:
                response = requests.post(POST_ENDPOINT, json={
                    "collectionName": "pings-gccd-indore",
                    "data": {
                        "name": personality,
                        "message": joke,
                        "timestamp": int(current_time * 1000)
                    }
                })
                if response.status_code == 200:
                    print(f"Successfully posted joke: {joke}")
                else:
                    print(f"Failed to post joke. Status code: {response.status_code}. Response content: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"RequestException occurred: {e}")
                print(traceback.format_exc())
            except Exception as e:
                print(f"Unexpected exception occurred: {e}")
                print(traceback.format_exc())
        else:
            print("No jokes found in the list.")

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
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5001))
