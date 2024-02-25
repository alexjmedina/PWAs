from flask import Flask, render_template, request, jsonify
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import yaml
import os
import openai

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
    with open('data.yaml', 'r') as f:
        data = yaml.safe_load(f)

    text_to_summarize = data.get('transcript', '')

    # Adjusted for GPT-4.0
    response = openai.Completion.create(
        model="text-davinci-004",  # Use the model identifier for GPT-4.0
        prompt=f"Summarize this text: {text_to_summarize}",
        max_tokens=150,  # Adjust max_tokens as needed
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    #summary = response.choices[0].text.strip()
    summary = response.get('choices')[0].get('text').strip()

    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)