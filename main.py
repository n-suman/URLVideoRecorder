import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# Dictionary to store registered URLs and their configuration data
registered_urls = {}

# Function to start recording from a given URL using FFmpeg
def start_recording(url, duration):
    output_filename = 'output.mp4'  # Change the filename and format as needed
    cmd = [
        'ffmpeg',
        '-i', url,
        '-t', str(duration),
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-y',  # Overwrite output file if it already exists
        output_filename,
    ]

    subprocess.run(cmd)

@app.route('/register', methods=['POST'])
def register_url():
    data = request.get_json()
    url = data.get('url')
    duration = data.get('duration')

    if not url or not duration:
        return jsonify({'error': 'URL and duration are required'}), 400

    registered_urls[url] = {'duration': duration}
    return jsonify({'message': 'URL registered successfully'}), 200

@app.route('/start_recording/<url>', methods=['POST'])
def start_recording_url(url):
    if url not in registered_urls:
        return jsonify({'error': 'URL not registered'}), 404

    duration = registered_urls[url]['duration']
    start_recording(url, duration)
    return jsonify({'message': f'Recording started for URL: {url}'}), 200

if __name__ == '__main__':
    app.run(debug=True)
