import sounddevice as sd
import numpy as np
from pyloudnorm import Meter

# 샘플 레이트 설정
fs = 48000
# 채널 수 설정 (1: 모노, 2: 스테레오)
channels = 1
# 버퍼 시간 설정 (400ms)
buffer_duration = 0.4
# 버퍼 크기 계산
buffer_size = int(fs * buffer_duration)

# 라우드니스 미터 초기화 (샘플 레이트에 맞게 설정)
meter = Meter(fs)

# 오디오 데이터 버퍼 초기화
audio_buffer = np.zeros(buffer_size, dtype=np.float32)

# 오디오 스트림 콜백 함수
def callback(indata, frames, time, status):
    global audio_buffer
    # 현재 입력된 오디오 데이터를 numpy 배열로 변환
    audio_data = np.frombuffer(indata, dtype=np.float32)
    # 버퍼에 새로운 오디오 데이터를 추가
    audio_buffer = np.append(audio_buffer, audio_data)
    
    # 버퍼가 설정한 크기를 초과할 경우 LUFS 계산
    if len(audio_buffer) >= buffer_size:
        # LUFS 계산
        loudness = meter.integrated_loudness(audio_buffer[:buffer_size])
        # 결과 출력
        print("Momentary LUFS:", loudness)
        # 버퍼 초기화 (새로운 오디오 데이터를 받기 위해)
        audio_buffer = np.zeros(buffer_size, dtype=np.float32)

# 오디오 스트림 시작
with sd.InputStream(channels=channels, samplerate=fs, callback=callback):
    sd.sleep(10000)  # 10초 동안 실행