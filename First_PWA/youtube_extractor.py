from flask import Flask, render_template, request, jsonify
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import yaml

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/extract', methods=['POST'])
def extract():
    url = request.json['url']
    yt = YouTube(url)
    title = yt.title or ''
    description = yt.description or ''
    video_id = url.split('=')[-1]
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = ' '.join([item['text'] for item in transcript_list]) if transcript_list else ''
    data = {'title': title, 'description': description, 'transcript': transcript_text}
    with open('data.yaml', 'w') as f:
        yaml.dump(data, f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
