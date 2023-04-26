from flask import Flask, render_template, request, send_file
import openai
import google.cloud.texttospeech as tts
import io
import os
from pydub import AudioSegment

# Set up OpenAI API credentials
openai.api_key = "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"

# Initialize Flask app
app = Flask(__name__)

# Define home route
@app.route('/')
def home():
    return render_template('home.html')

# Define generate_story route
@app.route('/generate_story', methods=['POST'])
def generate_story():
    # Get user inputs from HTML form
    age = int(request.form['age'])
    Protagonist_name = request.form['Protagonist_name']
    villain_name = request.form['villain_name']

    # Construct prompt using user inputs
    prompttext = f'Tell me a complete engaging short story full of colorful language and crisp visuals for {age} year olds with an antagonist named {Protagonist_name} and a villain named {villain_name}.'

    # Generate story using OpenAI API
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompttext,
        max_tokens=750,
        n=1,
        stop=None,
        temperature=0.5,
    )
    story = response.choices[0].text.replace('\n', '')

    # Convert story to audio using TTS API
    def text_to_wav(voice_name: str, text: str):
        language_code = "-".join(voice_name.split("-")[:2])
        text_input = tts.SynthesisInput(text=text)
        voice_params = tts.VoiceSelectionParams(
            language_code=language_code, name=voice_name
        )
        audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

        client = tts.TextToSpeechClient()
        response = client.synthesize_speech(
            input=text_input,
            voice=voice_params,
            audio_config=audio_config,
        )

        filename = f"{voice_name}.wav"
        with open(filename, "wb") as out:
            out.write(response.audio_content)
            print(f'Generated speech saved to "{filename}"')
        return filename

    # Generate audio file
    voice_name = "en-US-Wavenet-D"
    audio_file = text_to_wav(voice_name, story)

    # Send audio file to browser
    return render_template('story.html', story=story, audio_file=audio_file)

# Define route to serve audio file
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_file(filename, mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True)
