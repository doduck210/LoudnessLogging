from flask import Flask, request, send_from_directory, render_template, redirect, url_for, Response
import os, threading, time, sys
import main

app = Flask(__name__)

BASE_DIR = '/mnt/raid'
output_lines=[]

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
    if path[-1]!='/':
        path+='/'
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
    global output_lines
    output_lines = []  # 이전 출력 초기화

    # 스레드에서 sdiMain 실행
    thread = threading.Thread(target=run_sdi_main, args=(selected_date,))
    thread.start()

    return redirect(url_for('status'))

def run_sdi_main(selected_date):
    global output_lines
    # sdiMain 호출 전, 출력을 캡처하기 위해 stdout을 변경
    class StreamToList(object):
        def write(self, message):
            output_lines.append(message.strip())

        def flush(self):
            pass

    sys.stdout = StreamToList()

    main.sdiMain(
        scheduleDir='/mnt/raid/schedule/',
        audioDir='/mnt/jungbi',
        outputDir='/mnt/raid/data',
        chnlName='CleanPGM',
        outputAudioDir='/mnt/raid/audio',
        date=selected_date
    )

    sys.stdout = sys.__stdout__  # stdout 복원
    output_lines.append(f"{selected_date}에 대한 계산이 완료되었습니다.")

@app.route('/status')
def status():
    return render_template('status.html')

@app.route('/stream')
def stream():
    def generate():
        while True:
            if output_lines:
                yield f"data: {output_lines.pop(0)}\n\n"
            time.sleep(1)  # 1초마다 확인

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
