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
    # 解码 Base64 字符串
    audio_data = base64.b64decode(base64_audio)
    
    print(2)
    # 使用 pydub 从二进制数据创建音频段（这里假设是 MP3 格式，根据需要调整）
    audio_segment = AudioSegment.from_file(BytesIO(audio_data), format='webm', codec='opus')
    
    print(3)
    # 将 AudioSegment 对象导出为 WAV 格式的二进制数据
    wav_bytes = audio_segment.export(format="wav", sample_rate = SAMPLE_RATE, parameters=["-ar", "48000", "-ac", "1"])
    
    print(4)
    # 使用 scipy 读取 WAV 数据，获取采样率和音频数组
    sample_rate, audio_array = read_wav(BytesIO(wav_bytes.read()))
    
    print(5)
    # 确保音频数组是 numpy 格式
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

        sample_rate, audio_array = infer_from_audio(outgoingText, outgoingLanguage, "no-accent", None, base64_to_audio_array(wavAudioBase64),transcript, True)
        write_wav("First-Try.wav", SAMPLE_RATE, audio_array)
        
        return jsonify({"message": "Audio generated successfully!"}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400
    
    

if __name__ == '__main__':
    app.run(debug=True, port=5000)