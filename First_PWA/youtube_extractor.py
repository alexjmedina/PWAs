from flask import Flask, render_template, request, jsonify
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/extract', methods=['POST'])
def extract():
    url = request.json['url']
    yt = YouTube(url)
    title = yt.title
    description = yt.description
    video_id = url.split('=')[-1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    data = {'title': title, 'description': description, 'transcript': transcript}
    with open('data.json', 'w') as f:
        json.dump(data, f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
