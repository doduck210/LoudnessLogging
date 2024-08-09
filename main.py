import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, time
import getLoudness, scheduleRequest, utils
import spaceClearing
import openpyxl
import csv
import sys, os, traceback

def main(input_dir):
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
    print('ILKFS calculating for ', input_dir , ' channel has been started')

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
    nextDate = utils.get_next_day(startDate)
    startDate=utils.convert_date_format(startDate)
    nextDate=utils.convert_date_format(nextDate)

    ##해당날짜, 다음날짜 파일들 합치기
    video_files = utils.find_ts_files('/mnt/raid/video/'+startDate+'/'+input_dir)
    #video_files += utils.find_ts_files('/mnt/raid/video/'+nextDate+'/SBS-HD-NAMSAN/')
    concatenated_wav = '/mnt/raid/audio/' + startDate + input_dir + '.wav'
    if not os.path.exists(concatenated_wav):
        utils.concatenate_videos(video_files, concatenated_wav)

    # 시작시간 구하기
    sHours, sMinutes, sSeconds = map(int, EventList[0][2].text[:-3].split(":"))
    ss=timedelta(hours=sHours-4,minutes=sMinutes,seconds=sSeconds).total_seconds()
    # RF 보정값
    if input_dir=='SBS-HD-NAMSAN':
        ss+=0.5
    elif input_dir == 'SBS-UHD':
        ss-=2
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
        dd=Duration.total_seconds()
        if datetime_obj<morning4:
            ss+=dd
            continue
        morning7 = datetime.combine(today, time(7, 0, 0))
        if EndTime>morning7:
            ss+=dd
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
        with open('/mnt/raid/data/'+startDate+"/mlkfs"+StartTimeStr.replace(":","-")+input_dir+".csv","w",newline="") as file:
            writer = csv.writer(file)
            for item in mlkfs:
                writer.writerow([item])
        
    excel.save("/mnt/raid/data/Loudness_Report_"+startDate+input_dir+".xlsx")


def sdiMain(scheduleDir,audioDir,outputDir,chnlName, date="YYYY-MM-DD", outputAudioDir=""):
    ''' 편성파일과 오디오파일로 Loudness Report 생성
    
    Algorithm implementation under ITU_R BS.1770-3

    Generated Files
    ----------
    - [outputDir]/[chnlName]_Loudness_Report_[date].xlsx,   
    - [outputDir]/mlkfs/[date]/[chnlName]_[PGM IDX}_[PGM Start Time].csv   
    - (optional) [outputAudioDir]/[chnlName]_[PGM IDX]_[PGM Start Time].wav

    Parameters
    ----------
    scheduleDir : 
        편성파일위치
    audioDir :
         wav파일들 위치
    outputDir : 
        report생성할 위치
        해당위치에 "[채널명]_Loudness_Report_[날짜].xlsx"파일 생성
        I값 계산근거인 MLKFS값은 
        [해당위치]/mlkfs/[날짜] 폴더에 "[채널명]_[PGM_IDX}_[편성시작시간].csv" 으로생성
    chnlName : 
        채널명. 채널명으로 리포트 생성
    date : str
        "YYYY-MM-DD"
    outputAudioDir :
        프로그램별로 잘린 오디오 저장할 위치. 
        해당 위치에 날짜폴더 생기고 "[채널명]_[PGM IDX]_[편성시작시간].wav" 파일 생성
    '''
    #날짜 구하기
    if date=="YYYY-MM-DD":
        date=(datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d')
        dateStr=(datetime.now()-timedelta(days=1)).strftime('%Y%m%d')
    else : 
        dateStr=date.replace("-","")
    print(date , ' ILKFS calculating for ',chnlName, ' channel has been started')

    # xml (편성표) 파일 열기
    parser=ET.XMLParser(encoding="utf-8")
    if not os.path.exists(os.path.join(scheduleDir,dateStr+'.xml')):
        scheduleRequest.scheduleRequest(scheduleDir,date)
    scheduleFile = ET.parse(os.path.join(scheduleDir,dateStr+'.xml'),parser=parser)
    EventList = scheduleFile.getroot()
    EventListSize = len(EventList)
    if EventListSize==0 :
        print("No Schedule for ", date)
        sys.exit(1)

    # 오디오 파일 있는지 확인
    scheduleStart = datetime.strptime(f"{EventList[0][1].text} {EventList[0][2].text[:-3]}","%d/%m/%Y %H:%M:%S")
    scheduleEnd = datetime.strptime(f"{EventList[-1][1].text} {EventList[-1][2].text[:-3]}","%d/%m/%Y %H:%M:%S")
    if not utils.audioExistCheck(audioDir,scheduleStart,scheduleEnd):
        print("No recorded audio files maching with schedule")
        sys.exit(1)

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
            fileName=chnlName+"_"+EventIndex+"_"+StartTimeStr.replace(":","-"))
    
        print(EventIndex, ' / ', EventListSize, ' : ' ,lufs)
    
        # writing to excel
        row=[StartTimeStr,EndTimeStr,DurationStr,lufs,EventTitle,PGMID]
        sheet.append(row)
        # momentary lkfs saving
        mlkfsPath=os.path.join(outputMlkfsDir,chnlName+"_"+EventIndex+"_"+StartTimeStr.replace(":","-")+".csv")
        with open(mlkfsPath,"w",newline="") as file:
            writer = csv.writer(file)
            for item in mlkfs:
                writer.writerow([item])
        
    excel.save(outputFile)

if __name__=="__main__":
    try:
        main('SBS-HD-NAMSAN')

        try:
            date=sys.argv[1]
        except:
            date="YYYY-MM-DD"

        sdiMain(
            scheduleDir='/mnt/raid/schedule/'
            ,audioDir='/mnt/jungbi'
            ,outputDir='/mnt/raid/data'
            ,chnlName='CleanPGM'
            ,outputAudioDir='/mnt/raid/audio'
            )
        
        spaceClearing.videoClearing()
        spaceClearing.logClearing()

    except KeyboardInterrupt:
        pass
    except Exception:
        print(traceback.format_exc())
        utils.sendEmail(traceback.format_exc())