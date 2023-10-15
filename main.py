from flask import Flask, request, send_from_directory
import requests
import uuid
import os
import ffmpeg

app = Flask(__name__)

url = os.environ.get('URL')
port = os.environ.get('PORT')
playdir = os.environ.get('PLAY_DIRECTORY')
playurl = f"{url}:{port}/{playdir}/"

@app.route('/tts', methods=['POST'])
def tts():
    body = request.data.decode('utf-8')
    parsed_body = body.replace(',', ' ')
    if not body:
        return "Hello. Sorry we cannot do that request since you really have not given much to go on. you dingus.", 500
    return generate_tts(body), 200

@app.route('/play/<path:path>')
def play(path):
    return send_from_directory('storage', path)

def generate_tts(text):
    uid = str(uuid.uuid4())
    endpoint_url = 'http://185.130.224.61:5000/api/v1/chat'
    data = {
        # your data here
    }
    response = requests.post(endpoint_url, json=data)

    with open(f'storage/{uid}.ogg', 'wb') as file:
        file.write(response.content)

    convert(f'storage/{uid}.wav', f'storage/{uid}.ogg')

    # Cleaning up files
    def cleanup_files():
        os.remove(f'storage/{uid}.wav')
        os.remove(f'storage/{uid}.ogg')

    # Clean up after 60 seconds
    cleanup_files()
    return playurl + uid + '.ogg'

def convert(input, output):
    try:
        stream = ffmpeg.input(input)
        stream = ffmpeg.output(stream, output)
        ffmpeg.run(stream)
        print('Conversion successful')
    except ffmpeg.Error as e:
        print(f'An error occurred: {e.stderr}')

if __name__ == '__main__':
    app.run(port=5000)
