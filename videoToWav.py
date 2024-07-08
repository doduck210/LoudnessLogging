import subprocess
import os
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 폴더 내의 모든 mp4 파일을 찾아서 리스트로 반환
def find_ts_files(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.ts')]

def get_next_day(date_text):
    # 'dd/mm/yyyy' 형식의 날짜를 datetime 객체로 변환
    date_format = "%d/%m/%Y"
    date_obj = datetime.strptime(date_text, date_format)
    
    # datetime 객체에 하루를 추가
    next_day = date_obj + timedelta(days=1)
    
    # 수정된 날짜를 'dd/mm/yyyy' 형식의 문자열로 변환하여 반환
    next_day_text = next_day.strftime(date_format)
    return next_day_text

def convert_date_format(date_str):
    if len(date_str) != 10 or date_str[2] != '/' or date_str[5] != '/':
        return "잘못된 형식입니다. 'dd/mm/yyyy' 형식이어야 합니다."
    day, month, year = date_str.split('/')
    new_format = f"{year}-{month}-{day}"
    return new_format

# MP4를 wav파일로 바꾸는 함수
def convert_mp4_to_wav(input_mp4, output_wav):
    subprocess.run(['ffmpeg', '-i', input_mp4, '-vn', '-acodec', 'pcm_s16le', output_wav], check=True)

# MP4 파일들을 합치는 함수
def concatenate_videos(video_files, output_file):
    tmp_file = 'filelist.txt' # 임시 파일명으로 FFmpeg 파일 리스트 생성
    
    with open(tmp_file, 'w') as f: # 파일 리스트 작성
        for file in video_files:
            f.write(f"file '{file}'\n")
    
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', tmp_file, '-vn','-c:a', 'pcm_s16le', output_file], check=True)
    os.remove(tmp_file)

def split_wav_and_save(input_wav, start_time, duration, output_folder):
    # 출력 파일 이름 형성
    output_wav = os.path.join(output_folder, 'split_audio.wav')
    
    # 분할을 위한 FFmpeg 명령어 구성
    command = [
        'ffmpeg',
        '-i', input_wav,
        '-ss', start_time,  # 시작 시간
        '-t', str(duration),  # 지속 시간
        '-c', 'copy',
        output_wav
    ]
    
    # 해당 명령어 실행
    subprocess.run(command, check=True)
    
    print(f'Split audio saved to: {output_wav}')

def sendEmail():
    sender_email="duck@yonsei.ac.kr"
    receiver_email="duck@sbs.co.kr"
    f=open("/home/loger/Documents/LoudnessLogging/password","r")
    app_password=f.read()
    f.close()

    subject="Loudness Logger 에러 알림"
    text="Loudness Logger가 정상적으로 실행되지 못했습니다. 류덕형 혹은 정비실에 연락 부탁드립니다."
    html=f"<html><body><p>{text}</p></body></html>"

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
