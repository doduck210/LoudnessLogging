from flask import Flask, request, send_from_directory, render_template, redirect, url_for
import os
import main

app = Flask(__name__)

BASE_DIR = '/mnt/raid'

def get_files_and_dirs(path):
    items = os.listdir(path)
    files = []
    dirs = []
    for item in items:
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            dirs.append(item)
        else:
            files.append(item)
        dirs.sort()
        files.sort()
    return dirs, files

@app.route('/')
def index():
    return redirect(url_for('list_directory', path="data/"))

@app.route("/directory/<path:path>")
def list_directory(path):
    full_path = os.path.join(BASE_DIR, path)
    print(full_path)
    dirs, files = get_files_and_dirs(full_path)
    return render_template('directory.html', current_path=path, dirs=dirs, files=files)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(BASE_DIR, filename, as_attachment=True)

@app.route('/date', methods=['POST'])
def run_script():
    selected_date = request.form['date']
    main.sdiMain(
            scheduleDir='/mnt/raid/schedule/'
            ,audioDir='/mnt/jungbi'
            ,outputDir='/mnt/raid/data'
            ,chnlName='CleanPGM'
            ,outputAudioDir='/mnt/raid/audio'
            ,date=selected_date
            )
    # 선택된 날짜에 대해 Python 코드를 실행합니다.
    return f"{selected_date}에 해당하는 값을 다시 계산합니다"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
