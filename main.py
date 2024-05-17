import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import getLoudness
import videoToWav
import openpyxl
import csv
import os

# xml (편성표) 파일 열기
file = ET.parse('./data/mediaproxy_xml/20240304.xml')
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
video_files = videoToWav.find_mp4_files('./data/' + startDate)
video_files += videoToWav.find_mp4_files('./data/' + nextDate)
concatenated_wav = './data/tmp' + startDate + '.wav'
#videoToWav.concatenate_videos(video_files, concatenated_wav)

# 편성정보 프로그램별로 계산 및 엑셀에 기록
sHours, sMinutes, sSeconds = map(int, EventList[0][2].text[:-3].split(":"))
ss=timedelta(hours=sHours,minutes=sMinutes,seconds=sSeconds).total_seconds() + 1

# 편성정보 프로그램별로 계산 및 엑셀에 기록
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

    # get Loudness
    dd=Duration.total_seconds()
    lufs , mlkfs= getLoudness.splitAndLoud(concatenated_wav,ss,dd)
    print(EventIndex, ' / ', EventListSize, ' : ' ,lufs)
    ss+=dd

    # writing to excel
    row=[StartTimeStr,EndTimeStr,DurationStr,lufs,EventTitle,PGMID]
    sheet.append(row)
    # momentary lkfs saving
    with open('data/'+startDate+"/mlkfs"+StartTimeStr.replace(":","-")+".csv","w",newline="") as file:
        writer = csv.writer(file)
        for item in mlkfs:
            writer.writerow([item])
    
excel.save("./data/Loudness_Report_"+startDate+".xlsx")
#os.remove(concatenated_wav)