import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import subprocess
import os
import getLoudness

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

file = ET.parse('./mediaproxy_xml/20240304.xml')
EventList = file.getroot()
EventListSize = len(EventList)

for EventInfo in EventList:
    EventIndex = EventInfo[0].text
    OnAirDate = EventInfo[1].text # DD/MM/YYYY
    StartTimeStr = EventInfo[2].text[:-3] # hh:mm:ss
    DurationStr = EventInfo[3].text[:-3] # hh:mm:ss
    PGMID = EventInfo[4].text
    EventTitle = EventInfo[5].text

    # calculate End Time
    timedateStr = f"{OnAirDate} {StartTimeStr}"
    StartTime = datetime.strptime(timedateStr,"%d/%m/%Y %H:%M:%S")
    dHours, dMinutes, dSeconds = map(int, DurationStr.split(":"))
    Duration = timedelta(hours=dHours,minutes=dMinutes,seconds=dSeconds)
    EndTime = StartTime+Duration
    EndTimeStr = EndTime.strftime("%H:%M:%S")
    print(StartTime, EndTime)

    split_wav_and_save('final_output.wav',StartTimeStr,DurationStr,'data')
    print("########################################")
    print(getLoudness.getLoudness('./data/split_audio.wav'))
    print("########################################")

    #print(StartTimeStr , DurationStr , EndTimeStr)
