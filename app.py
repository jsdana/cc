from flask import Flask, request, send_file
from flask_cors import CORS
from google.cloud import texttospeech
import os
from datetime import datetime
import json
from google.oauth2 import service_account

app = Flask(__name__)
CORS(app)

# Carrega as credenciais a partir da variável de ambiente
credentials_info = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
credentials = service_account.Credentials.from_service_account_info(credentials_info)

client = texttospeech.TextToSpeechClient()

@app.route('/synthesize', methods=['POST'])
def synthesize():
    content = request.json.get('text', '')

    if not content:
        return {"error": "No text provided"}, 400

    # Configure a solicitação de síntese
    synthesis_input = texttospeech.SynthesisInput(text=content)

    # Selecione o tipo de voz e o idioma (português brasileiro)
    voice = texttospeech.VoiceSelectionParams(
        language_code="pt-BR",
        name="pt-BR-Wavenet-B",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Selecione o tipo de áudio a ser retornado
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Realize a solicitação de síntese de texto para fala
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Gera um timestamp formatado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_{timestamp}.mp3"

    # Salve a saída de áudio em um arquivo temporário
    with open(output_filename, "wb") as out:
        out.write(response.audio_content)

    return send_file(output_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
