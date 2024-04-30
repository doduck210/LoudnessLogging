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

file = ET.parse('./data/mediaproxy_xml/20240304.xml')
EventList = file.getroot()
EventListSize = len(EventList)

# 날짜와 다음날짜 구하기
startDate = EventList[0][1].text
nextDate = get_next_day(startDate)
startDate=convert_date_format(startDate)
nextDate=convert_date_format(nextDate)
print(startDate, nextDate)

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
    #print(StartTime, EndTime)

    #print(StartTimeStr , DurationStr , EndTimeStr)
