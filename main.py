from flask import Flask, request, send_from_directory
import uuid
import os
import ffmpeg
import requests
import subprocess

app = Flask(__name__)

url = os.environ.get('URL')
port = os.environ.get('PORT')
playdir = os.environ.get('PLAY_DIRECTORY')
if playdir is None:
    playdir = 'null'
playurl = f"{url}:{port}/{playdir}/"

@app.route('/tts', methods=['POST'])
def tts():
    body = request.data.decode('utf-8')
    parsed_body = body.replace(',', ' ')
    print(parsed_body)
    if not body:
        return "Hello. Sorry we cannot do that request since you really have not given much to go on. you dingus.", 500
    return generate_tts(parsed_body), 200

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

    with open(f'storage/{uid}.txt', 'w') as text_file:
        text_file.write(response.content.decode('utf-8'))

    # Using subprocess to call espeak command
    subprocess.run(['espeak', '-ven', '+f3', '-s150', f'-w storage/{uid}.wav', response.content.decode('utf-8')])

    convert(f'storage/{uid}.wav', f'storage/{uid}.ogg')

    # Cleaning up files
    def cleanup_files():
        os.remove(f'storage/{uid}.wav')
        os.remove(f'storage/{uid}.ogg')

    # Clean up after 60 seconds
    cleanup_files()
    return playurl + uid + '.ogg'

def generate_tts(text):
    uid = str(uuid.uuid4())
    endpoint_url = 'http://185.130.224.61:5000/api/v1/chat'
    data = {
        "user_input": text,
        "max_new_tokens": 250,
        "auto_max_new_tokens": False,
        "max_tokens_second": 0,
        "history": {"internal": [], "visible": []},
        "mode": "instruct",
        "character": "Example",
        "instruction_template": "Vicuna-v1.1",
        "your_name": "You",
        "regenerate": False,
        "_continue": False,
        "chat_instruct_command": "Continue the chat dialogue below. Write a single reply for the character \"\".\n\n",
        "preset": "None",
        "do_sample": True,
        "temperature": 0.7,
        "top_p": 0.1,
        "typical_p": 1,
        "epsilon_cutoff": 0,
        "eta_cutoff": 0,
        "tfs": 1,
        "top_a": 0,
        "repetition_penalty": 1.18,
        "repetition_penalty_range": 0,
        "top_k": 40,
        "min_length": 0,
        "no_repeat_ngram_size": 0,
        "num_beams": 1,
        "penalty_alpha": 0,
        "length_penalty": 1,
        "early_stopping": False,
        "mirostat_mode": 0,
        "mirostat_tau": 5,
        "mirostat_eta": 0.1,
        "grammar_string": "",
        "guidance_scale": 1,
        "negative_prompt": "",
        "seed": -1,
        "add_bos_token": True,
        "truncation_length": 2048,
        "ban_eos_token": False,
        "custom_token_bans": "",
        "skip_special_tokens": True,
        "stopping_strings": []
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
