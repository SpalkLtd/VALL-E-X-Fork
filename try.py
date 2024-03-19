import base64
from io import BytesIO

import numpy as np
from utils.generation import SAMPLE_RATE
from scipy.io.wavfile import write as write_wav
from utils.prompt_making import make_prompt
from flask import Flask, jsonify, request, send_file
import torch
import langid
from vocos import Vocos
from data.collation import get_text_token_collater
langid.set_languages(['en', 'zh', 'ja'])
from pydub import AudioSegment
from scipy.io.wavfile import read as read_wav
from launch_ui import infer_from_audio
from scipy.io.wavfile import write as write_wav



app = Flask(__name__)

def base64_to_audio_array(base64_audio):
    print(1)
    audio_data = base64.b64decode(base64_audio)
    
    print(2)
    audio_segment = AudioSegment.from_file(BytesIO(audio_data), format='webm', codec='opus')
    
    print(3)
    wav_bytes = audio_segment.export(format="wav", parameters=["-ar", "48000", "-ac", "1"], codec="pcm_s32le")

    print(4)
    sample_rate, audio_array = read_wav(BytesIO(wav_bytes.read()))
    
    print(5)
    audio_array = np.array(audio_array)
    
    return sample_rate, audio_array

# generate audio from text
@app.route('/generate_audio', methods=['POST'])
def generate_audio ():
    if request.is_json:
        data = request.get_json()
        outgoingText = data.get('OutgoingText', '')
        outgoingLanguage = data.get('OutgoingLanguage', '')
        transcript = data.get('Transcript', '')
        wavAudioBase64 = data.get('WavAudioBase64', '')

        audio_array = infer_from_audio(outgoingText, outgoingLanguage, "no-accent", None, base64_to_audio_array(wavAudioBase64),transcript, True)
        encodeAudioArray = base64.b64encode(audio_array)

        write_wav("First-Try.wav", SAMPLE_RATE, audio_array)
        
        return jsonify({"message": "Audio generated successfully!", "WavAudioBase64" : encodeAudioArray, "SampleRate": SAMPLE_RATE}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400
    
    

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
