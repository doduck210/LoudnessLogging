import subprocess
import os
from datetime import datetime, timedelta

# 폴더 내의 모든 mp4 파일을 찾아서 리스트로 반환
def find_mp4_files(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.mp4')]

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
    subprocess.run(['ffmpeg', '-i', input_mp4, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', output_wav], check=True)

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