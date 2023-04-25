from flask import Flask, render_template, request, make_response
from google.cloud import texttospeech
import openai
import io
import base64

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
    antagonist_name = request.form['antagonist_name']
    villain_name = request.form['villain_name']

    # Construct prompt using user inputs
    prompttext = f'Tell me a complete engaging short story full of colorful language and crisp visuals for {age} year olds with an antagonist named {antagonist_name} and a villain named {villain_name}.'

    # Generate story using OpenAI API
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompttext,
        max_tokens=750,
        n=1,
        stop=None,
        temperature=0.5,
    )
    story = response.choices[0].text.replace('\n', ' ')

    # Convert story to audio using TTS API
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=story)
    voice = texttospeech.VoiceSelectionParams(
        language_code='en-US', ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # Convert audio binary data to playable audio format
    audio_data = response.audio_content
    audio_base64 = base64.b64encode(audio_data).decode('ascii')
    audio_element = f'<audio controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'

    # Create HTML response with audio element and story text
    story = story.replace('\n', '<br>')
    response_html = f'<p>{story}</p>{audio_element}'
    return make_response(response_html)

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
