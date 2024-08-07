import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, time
import getLoudness
import utils
import spaceClearing
import openpyxl
import csv
import sys, os, traceback

def sdiMain(scheduleDir,audioDir,outputDir,chnlName, outputAudioDir=""):
    '''
    
    '''
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
    print('ILKFS calculating for SDI channel has been started')

    # xml (편성표) 파일 열기
    parser=ET.XMLParser(encoding="utf-8")
    file = ET.parse(os.path.join(scheduleDir,yesterdayStr+'.xml'),parser=parser)
    EventList = file.getroot()
    EventListSize = len(EventList)

    # Excel Report File
    excel = openpyxl.Workbook()
    sheet = excel.active
    columns = ["Start Time","End Time","Duration","ILKFS","Title","ID"]
    sheet.append(columns)

    # 날짜와 다음날짜 구하기
    startDate = EventList[0][1].text
    nextDate = utils.get_next_day(startDate)
    startDate=utils.convert_date_format(startDate)
    nextDate=utils.convert_date_format(nextDate)
    
    # output 폴더 및 파일명 설정
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    outputFile=os.path.join(outputDir,chnlName+"_Loudness_Report_"+startDate+".xlsx")
    outputMlkfsDir=os.path.join(outputDir,"mlkfs")
    if not os.path.exists(outputMlkfsDir):
        os.makedirs(outputMlkfsDir)
    outputMlkfsDir=os.path.join(outputMlkfsDir,startDate)
    if not os.path.exists(outputMlkfsDir):
        os.makedirs(outputMlkfsDir)
    outputAudioDir=os.path.join(outputAudioDir,startDate)
    if not os.path.exists(outputAudioDir):
        os.makedirs(outputAudioDir)

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
        
        # calc loudness
        lufs , mlkfs = getLoudness.programLoudness(
            inputDir=audioDir,
            startTime=StartTime,
            endTime=EndTime,
            correctionTime=1.8,
            save=True,
            outputDir=outputAudioDir,
            fileName=EventIndex+"_"StartTimeStr.replace(":","-"))
        
        print(EventIndex, ' / ', EventListSize, ' : ' ,lufs)

        # writing to excel
        row=[StartTimeStr,EndTimeStr,DurationStr,lufs,EventTitle,PGMID]
        sheet.append(row)
        # momentary lkfs saving
        mlkfsPath=os.path.join(outputMlkfsDir,chnlName+EventIndex+"_"+StartTimeStr.replace(":","-")+"csv")
        with open(mlkfsPath,"w",newline="") as file:
            writer = csv.writer(file)
            for item in mlkfs:
                writer.writerow([item])
        
    excel.save(outputFile)

if __name__ == "__main__":
    sdiMain('/mnt/raid/schedule/','/mnt/jungbi','/mnt/raid/data','CleanPGM','/mnt/raid/audio')