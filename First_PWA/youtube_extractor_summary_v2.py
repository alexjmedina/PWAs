from flask import Flask, render_template, request, jsonify
import os
import yaml
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
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
        transcript_text = ' '.join([item['text'] for item in transcript_list])
    except TranscriptsDisabled:
        transcript_text = "Transcript not available."
    data = {'title': title, 'description': description, 'transcript': transcript_text}
    with open('data.yaml', 'w') as f:
        yaml.dump(data, f)
    return jsonify(data)

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        with open('data.yaml', 'r') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        return jsonify({'error': 'Data file not found. Please extract data first.'}), 404

    text_to_summarize = data.get('transcript', '')
    
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize this text: {text_to_summarize}"}
        ],
        max_tokens=150,
        temperature=0.7,
    )

    # Simplified access to summary content
    try:
        summary_content = response.choices[0].message['content'] if response.choices else "Summary not available."
    except AttributeError:
        summary_content = "Summary not available."

    return jsonify({'summary': summary_content})

if __name__ == '__main__':
    app.run(debug=True)
