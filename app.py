import os
from flask import Flask, request, send_file, jsonify, render_template
from moviepy.video.io.VideoFileClip import VideoFileClip

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CHUNK_FOLDER = 'chunks'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHUNK_FOLDER, exist_ok=True)

# Функция для разбиения видео
def split_video(filename):
    video = VideoFileClip(filename)
    duration = video.duration  # Продолжительность видео в секундах
    chunks = []
    start_time = 0
    chunk_duration = 120  # Длительность каждого фрагмента (2 минуты)

    while start_time < duration:
        end_time = min(start_time + chunk_duration, duration)
        
        # Если последняя часть меньше 50 секунд, добавляем её к предыдущей
        if duration - end_time < 50 and duration - start_time > chunk_duration:
            end_time = duration
        
        chunk_filename = f"{CHUNK_FOLDER}/chunk_{int(start_time)}.mp4"
        video.subclip(start_time, end_time).write_videofile(chunk_filename, codec="libx264")
        chunks.append(chunk_filename)
        start_time = end_time
    
    video.close()
    return chunks

# Главная страница с интерфейсом
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    try:
        chunks = split_video(filepath)
        return jsonify({'chunks': chunks}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<chunk_name>', methods=['GET'])
def download_chunk(chunk_name):
    chunk_path = os.path.join(CHUNK_FOLDER, chunk_name)
    if os.path.exists(chunk_path):
        return send_file(chunk_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
