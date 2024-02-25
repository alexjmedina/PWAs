from flask import Flask, render_template, request, jsonify
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import yaml
import os
import openai
from openai import OpenAI

app = Flask(__name__)

# Set your OpenAI API key here from your environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    url = request.json['url']
    yt = YouTube(url)
    title = yt.title or ''
    description = yt.description or ''
    video_id = url.split('=')[-1]
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([item['text'] for item in transcript_list]) if transcript_list else ''
    except:
        transcript_text = "Transcript not available."
    data = {'title': title, 'description': description, 'transcript': transcript_text}
    with open('data.yaml', 'w') as f:
        yaml.dump(data, f)
    return jsonify(data)

@app.route('/summarize', methods=['POST'])
def summarize():
    # Assuming you've loaded your data into `data` from 'data.yaml'
    # and it includes a 'transcript' key with the text to summarize.
    with open('data.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    text_to_summarize = data.get('transcript', '')
    
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Adjust according to the latest available version
        messages=f"Summarize this text: {text_to_summarize}",
        max_tokens=150,
        temperature=0.7,
    )
    #summary = response.choices[0].text.strip()
    #summary = response.get('choices')[0].get('text').strip()
    summary = response.choices[0].text.strip()

    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)
