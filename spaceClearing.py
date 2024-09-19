import os
import datetime
import shutil

def oldClearing(path, days):
    # 현재 날짜
    current_time = datetime.now()
    # days 전 날짜
    cutoff_date = current_time - datetime.timedelta(days=days)

    # 디렉토리 내 모든 파일 및 디렉토리 검사
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        
        # 항목의 생성일자 가져오기
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(item_path))
        
        # days 이상된 항목 삭제
        if creation_time < cutoff_date:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)  # 디렉토리 삭제
                print(f"삭제됨: {item_path} (디렉토리)")
            else:
                os.remove(item_path)  # 파일 삭제
                print(f"삭제됨: {item_path} (파일)")

def serverClearing():
    # 오디오 삭제
    oldClearing('/mnt/raid/audio',3)
    # 레코딩 삭제
    oldClearing('mnt/raid/recording/SBS_HD',100)


def recordClearing(chnl):
    recordDir = os.path.join('/mnt/raid/recording',chnl)

    # old standard is set as 3 days
    recordOldStandard = datetime.date.today() - datetime.timedelta(days=100)

    for files in os.listdir(recordDir):
        fileDateStr = files[:10].split('-')
        fileDate = datetime.date( int(fileDateStr[0]), int(fileDateStr[1]), int(fileDateStr[2]))
        if fileDate < recordOldStandard :
            folderPath = os.path.join(recordDir,files)
            shutil.rmtree(folderPath)
            print(f"Deleted Recording File : {files}")

def scheduleClearing(chnl):
    scheduleDir = os.path.join('/mnt/raid/recording',chnl)

    # old standard is set as 3 days
    scheduleOldStandard = datetime.date.today() - datetime.timedelta(days=3650)

    for files in os.listdir(scheduleDir):
        fileDateStr = files[:10].split('-')
        fileDate = datetime.date( int(files[0:4]), int(files[4:6]), int(files[6:8]))
        if fileDate < scheduleOldStandard :
            folderPath = os.path.join(scheduleDir,files)
            shutil.rmtree(folderPath)
            print(f"Deleted Recording File : {files}")

def audioClearing():
    audioDir = '/mnt/raid/audio'

    audioOldStandard = datetime.date.today() - datetime.timedelta(days=50)

    for files in os.listdir(audioDir):
        fileDateStr = files[:10].split('-')
        fileDate = datetime.date( int(fileDateStr[0]), int(fileDateStr[1]), int(fileDateStr[2]))
        if fileDate < audioOldStandard :
            folderPath = os.path.join(audioDir,files)
            shutil.rmtree(folderPath)
            print(f"Deleted File : {files}")

def logClearing():
    logDir="/home/logger/Documents/LoudnessLogging/data"
    
    logOldStandard = datetime.date.today() - datetime.timedelta(days=180)

    for files in os.listdir(logDir):
        if not files.endswith(".log"):
            continue
        fileDateStr = files[:-4].split('-')
        logDate = datetime.date( int(fileDateStr[0]), int(fileDateStr[1]), int(fileDateStr[2]))
        if logDate < logOldStandard :
            filePath = os.path.join(logDir,files)
            os.remove(filePath)
            print(f"Deleted File : {files}")
        
if __name__ == '__main__':
    print('N/A')