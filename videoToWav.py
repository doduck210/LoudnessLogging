import subprocess
import os

# 폴더 내의 모든 mp4 파일을 찾아서 리스트로 반환하는 함수
def find_mp4_files(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.mp4')]

# MP4 파일들을 합치는 함수
def concatenate_videos(video_files, output_file):
    # 임시 파일명으로 FFmpeg 파일 리스트 생성
    tmp_file = 'filelist.txt'
    # 파일 리스트 작성
    with open(tmp_file, 'w') as f:
        for file in video_files:
            f.write(f"file '{file}'\n")
    
    # FFmpeg를 이용해서 비디오 파일 합치기
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', tmp_file, '-c', 'copy', output_file], check=True)

    # 임시 파일 삭제
    os.remove(tmp_file)
    
# 폴더 내의 모든 mp4 파일을 찾음
video_files = find_mp4_files('./2024-03-04') 
# 모든 비디오 파일을 합친 후의 임시 비디오 파일 이름
concatenated_video_file = 'concatenated_temp.mp4'

concatenate_videos(video_files, concatenated_video_file)

def convert_mp4_to_wav(input_mp4, output_wav):
    subprocess.run(['ffmpeg', '-i', input_mp4, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', output_wav], check=True)

# 최종 WAV 파일 이름
output_wav_file = 'final_output.wav'

convert_mp4_to_wav(concatenated_video_file,output_wav_file)