import streamlit as st
import boto3
import openai
import speech_recognition as sr

# Set up Amazon Polly credentials
polly_client = boto3.Session(
   aws_access_key_id="AKIAWRXPYOZF5XXZCZNB",
    aws_secret_access_key="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",
    region_name="us-east-1"
).client('polly')

# Set up OpenAI credentials
openai.api_key = "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"

# Define function to generate speech using Amazon Polly
def generate_speech(text, voice_id):
    response = polly_client.synthesize_speech(
        Engine='neural',
        OutputFormat='mp3',
        Text=text,
        TextType='text',
        VoiceId=voice_id
    )
    return response['AudioStream'].read()

# Define OpenAI GPT-3.5 API parameters
api_messages = []
openai.api_endpoint = "https://api.openai.com"
openai_model = "text-davinci-002"
openai_prompt =  "You are acting as an English teacher for someone who wants to prepare for IELTS exam"
openai_temperature = 0.75
openai_max_tokens = 700
openai_n = 1

# Define function to generate response using OpenAI GPT-3.5 API
def generate_response(prompt):
    response = openai.Completion.create(
        engine=openai_model,
        prompt=prompt,
        max_tokens=openai_max_tokens,
        temperature=openai_temperature,
        n=openai_n,
        stream=False
    )
    message = response.choices[0].text.strip()
    api_messages.append(message)
    return message

# Get available voices from Amazon Polly
voices = {}
try:
    response = polly_client.describe_voices(LanguageCode='en-US')
    for voice in response['Voices']:
        voices[voice['Name']] = {'id': voice['Id'], 'language': voice['LanguageName']}
except Exception as e:
    st.error("Error getting voices: {}".format(e))

# Streamlit app code
st.set_page_config(page_title="Voice Assistant")
# Set up SpeechRecognition
r = sr.Recognizer()
st.title("Your English Teacher")
st.write("I am friendly AI that can teach you English faster:")
# Define function to convert speech to text
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    try:
        print("Transcription: " + r.recognize_google(audio))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    return r.recognize_google(audio)

text_input = st.text_input("Your question here:", key="question")
if st.button("Record"):
    text_input = speech_to_text()
    st.write("You said: ", text_input)

voice_selectbox = st.selectbox("Select voice:", list(voices.keys()))
voice_id = voices[voice_selectbox]['id']


if st.button("Ask"):
    # Generate response using OpenAI GPT-3.5 API
    answer = generate_response(openai_prompt + " " + text_input)
    st.write("Answer:", answer)
    
    # Synthesize response into speech using Amazon Polly
audio_file = st.audio(generate_speech(answer, voice_id), format='audio/mp3')