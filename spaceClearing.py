import os
import datetime
import shutil

def videoClearing():
    videoDir = '/mnt/raid/video'

    # old standard is set as 3 days
    videoOldStandard = datetime.date.today() - datetime.timedelta(days=2)

    for folder in os.listdir(videoDir):
        folderDateStr = folder.split('-')
        folderDate = datetime.date( int(folderDateStr[0]), int(folderDateStr[1]), int(folderDateStr[2]))
        if folderDate < videoOldStandard :
            folderPath = os.path.join(videoDir,folder)
            shutil.rmtree(folderPath)
            print(f"Deleted Folder : {folder}")

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
        fileDateStr = files[:-4].split('-')
        logDate = datetime.date( int(fileDateStr[0]), int(fileDateStr[1]), int(fileDateStr[2]))
        if logDate < logOldStandard :
            filePath = os.path.join(logDir,files)
            os.remove(filePath)
            print(f"Deleted File : {files}")
        
if __name__ == '__main__':
    print('N/A')