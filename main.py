import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, time
import getLoudness
import videoToWav
import spaceClearing
import openpyxl
import csv
import sys, os

#날짜 구하기
today=datetime.now()
before=0
try:
    before=int(sys.argv[1])
    if before>=50 or before<0:
        print("Audio are archived only for 50 days")
        os._exit(0)
    today=today-timedelta(days=before)
except:
    print("No input detected. Default is yesterday")
yesterday=today-timedelta(days=1)
todayStr=today.strftime('%Y%m%d')
yesterdayStr=yesterday.strftime('%Y%m%d')

# xml (편성표) 파일 열기
parser=ET.XMLParser(encoding="utf-8")
file = ET.parse('/mnt/raid/schedule/'+yesterdayStr+'.xml',parser=parser)
EventList = file.getroot()
EventListSize = len(EventList)

# Excel Report File
excel = openpyxl.Workbook()
sheet = excel.active
columns = ["Start Time","End Time","Duration","ILKFS","Title","ID"]
sheet.append(columns)

# 날짜와 다음날짜 구하기
startDate = EventList[0][1].text
nextDate = videoToWav.get_next_day(startDate)
startDate=videoToWav.convert_date_format(startDate)
nextDate=videoToWav.convert_date_format(nextDate)

##해당날짜, 다음날짜 파일들 합치기
video_files = videoToWav.find_ts_files('/mnt/raid/video/'+startDate+'/SBS-HD-NAMSAN/')
#video_files += videoToWav.find_ts_files('/mnt/raid/video/'+nextDate+'/SBS-HD-NAMSAN/')
concatenated_wav = '/mnt/raid/audio/' + startDate + '.wav'
if not os.path.exists(concatenated_wav):
    videoToWav.concatenate_videos(video_files, concatenated_wav)

# 시작시간 구하기
sHours, sMinutes, sSeconds = map(int, EventList[0][2].text[:-3].split(":"))
ss=timedelta(hours=sHours-4,minutes=sMinutes,seconds=sSeconds).total_seconds() + 1
if not os.path.exists('/mnt/raid/data/'+startDate):
    os.makedirs('/mnt/raid/data/'+startDate)

# 편성정보 프로그램별로 계산 및 엑셀에 기록
for EventInfo in EventList:
    EventIndex = EventInfo[0].text
    OnAirDate = EventInfo[1].text # DD/MM/YYYY
    StartTimeStr = EventInfo[2].text[:-3] # hh:mm:ss
    DurationStr = EventInfo[3].text[:-3] # hh:mm:ss
    PGMID = EventInfo[4].text
    EventTitle = EventInfo[5].text
    descriptive = EventInfo[6].text

    # calculate End Time
    timedateStr = f"{OnAirDate} {StartTimeStr}"
    StartTime = datetime.strptime(timedateStr,"%d/%m/%Y %H:%M:%S")
    dHours, dMinutes, dSeconds = map(int, DurationStr.split(":"))
    Duration = timedelta(hours=dHours,minutes=dMinutes,seconds=dSeconds)
    EndTime = StartTime+Duration
    EndTimeStr = EndTime.strftime("%H:%M:%S")

    # <4시, 익일 7시< 인 시간대는 제외
    date_obj = datetime.strptime(OnAirDate, "%d/%m/%Y")
    time_obj = datetime.strptime(StartTimeStr, "%H:%M:%S")
    datetime_obj = datetime.combine(date_obj, time_obj.time())
    morning4 = datetime.combine(yesterday, time(4, 0, 0))
    if datetime_obj<morning4:
        continue
    morning7 = datetime.combine(today, time(7, 0, 0))
    if EndTime>morning7:
        continue

    # get Loudness
    dd=Duration.total_seconds()
    lufs , mlkfs= getLoudness.splitAndLoud(concatenated_wav,ss,dd)
    print(EventIndex, ' / ', EventListSize, ' : ' ,lufs)
    ss+=dd

    # writing to excel
    row=[StartTimeStr,EndTimeStr,DurationStr,lufs,EventTitle,PGMID]
    sheet.append(row)
    # momentary lkfs saving
    with open('/mnt/raid/data/'+startDate+"/mlkfs"+StartTimeStr.replace(":","-")+".csv","w",newline="") as file:
        writer = csv.writer(file)
        for item in mlkfs:
            writer.writerow([item])
    
excel.save("/mnt/raid/data/Loudness_Report_"+startDate+".xlsx")
spaceClearing.videoClearing()
spaceClearing.logClearing()