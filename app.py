from flask import Flask, render_template, request, jsonify, send_from_directory , after_this_request, send_file
import yt_dlp
import os

app = Flask(__name__)

if not os.path.exists('downloads'):
    os.makedirs('downloads')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_info', methods=['POST'])
def fetch_info():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)
        return jsonify({
            'title': info.get('title'),
            'thumbnail': info.get('thumbnail')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    quality = data.get('quality', 'best')
    download_mp3 = data.get('download_mp3', False)

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        if download_mp3:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }
        else:
            ydl_opts = {
                'format': quality,
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'merge_output_format': 'mp4',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)

        filename_only = os.path.basename(filename)

        if download_mp3:
            filename_only = os.path.splitext(filename_only)[0] + ".mp3"

        return jsonify({
            'title': info.get('title'),
            'filepath': f'/downloads/{filename_only}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/downloads/<path:filename>')
def serve_download(filename):
    return send_from_directory('downloads', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
