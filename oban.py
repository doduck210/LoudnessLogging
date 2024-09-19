from flask import Flask, request, send_from_directory, render_template, redirect, url_for, Response
import os, threading, time, sys, shutil, re
import main
import xml.etree.ElementTree as ET
from xml.dom import minidom

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

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "파일이 없습니다.", 400
    file = request.files['file']
    if file.filename == '':
        return "파일 이름이 없습니다.", 400
    
    # 현재 경로를 가져옵니다.
    current_path = request.form.get('current_path', '')
    full_upload_path = os.path.join(BASE_DIR, current_path, file.filename)
    
    file.save(full_upload_path)
    return redirect(url_for('list_directory', path=current_path))

@app.route('/delete_dir/<path:dirname>', methods=['POST'])
def delete_directory(dirname):
    dir_path = os.path.join(BASE_DIR, dirname)
    try:
        shutil.rmtree(dir_path)  # 디렉토리와 그 안의 모든 내용을 삭제
        return redirect(url_for('list_directory', path='audio/'))
    except FileNotFoundError:
        return "디렉토리를 찾을 수 없습니다.", 404
    except Exception as e:
        return f"오류 발생: {str(e)}", 400

@app.route('/date', methods=['POST'])
def run_script():
    selected_date = request.form['date']
    global output_lines
    output_lines = []  # 이전 출력 초기화

    # 스레드에서 sdiMain 실행
    thread = threading.Thread(target=run_sdi_main, args=(selected_date,))
    thread.start()

    return redirect(url_for('status'))

@app.route('/view_xml/<path:filename>')
def view_xml(filename):
    full_path = os.path.join(BASE_DIR, filename)
    xml_content = read_xml_file(full_path)
    return render_template('edit_xml.html', xml_content=xml_content, filename=filename)

@app.route('/save_xml/<path:filename>', methods=['POST'])
def save_xml(filename):
    xml_data = request.form['xml_content']
    full_path = os.path.join(BASE_DIR, filename)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(xml_data)
    
    return redirect(url_for('list_directory', path='schedule'))

def read_xml_file(filepath):
    tree = ET.parse(filepath,ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
    if bool(re.search(r'\n\s*<', xml_str)):
        return xml_str
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ")
    return pretty_xml_str

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
        audioDir='/mnt/raid/recording/SBS_HD',
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
