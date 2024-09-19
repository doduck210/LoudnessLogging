import lkfs
import soundfile as sf
import subprocess, os, sys, traceback
from datetime import datetime, timedelta


def getLoudness(file):
    data, rate = sf.read(file) #data.shape : (길이, 채널수) 
    meter = lkfs.Meter(rate)
    loudness, mlkfs = meter.integrated_loudness(data)
    return loudness, mlkfs

def splitAndLoud(file_path,start_time,duration):
    fileName="/home/logger/Documents/LoudnessLogging/data/"+str(start_time)+"tmpWav.wav"
    subprocess.run(['ffmpeg','-i',file_path,'-ss',str(start_time),'-t',str(duration),'-c','copy',fileName],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    lufs, mlkfs = getLoudness(fileName)
    os.remove(fileName)
    return lufs, mlkfs


def programLoudness(inputDir, startTime, endTime, correctionTime=0, save=True, outputDir="", fileName="tmpProgram"):
    """ 프로그램 시간 따른 Loudness값 return
    
    Parameters
    ----------
    inputDir :
        location of wav files
    startTime : datetime 
        schedule start time
    endTime : datetime
        schedule end time
    correctionTime : float
        correction seconds. 보정값(초)

    save : bool
        weather to save program(cutted) wav file
    outputDir : 
        location to save program(cutted) wav file
    fileName : 
        fileName of program(cutted) wav file
    """
    # 보정값 처리
    startTime+=timedelta(seconds=correctionTime)
    endTime+=timedelta(seconds=correctionTime)
    # 프로그램 wav파일 이름
    cutWav = os.path.join(outputDir,fileName+".wav")
    if os.path.exists(cutWav):
        ilkfs,mlkfs = getLoudness(cutWav)
        return ilkfs, mlkfs
    # 파일리스트 찾기 위한 첫파일, 끝파일
    startHourStr=startTime.strftime("%Y-%m-%d_%H.00.00")
    endHourStr=endTime.strftime("%Y-%m-%d_%H.00.00")
    # 파일리스트 가져오기
    fileList=[os.path.join(inputDir, file) for file 
              in os.listdir(inputDir) if file >= (startHourStr+".wav") and file <= (endHourStr+".wav")]
    
    # 첫파일에서 시작부분    
    ss=timedelta(minutes=startTime.minute,seconds=startTime.second).total_seconds()+correctionTime-int(correctionTime)
    # 끝파일에서 끝부분
    to=timedelta(minutes=endTime.minute,seconds=endTime.second).total_seconds()+correctionTime-int(correctionTime)
    
    try :
        if len(fileList) < 2 : # 파일 하나면
            subprocess.run(
                ['ffmpeg', '-i',fileList[0],'-ss',str(ss),'-to',str(to),
                '-vn', '-af', 'pan=2c|c0=c0|c1=c1', '-c:a', 'pcm_s16le',cutWav]
                ,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                ,check=True)

        else : # 파일 여러개면 처음과 끝파일을 임시로 만들고 tmplist임시로 만들어서 처리
            # 첫파일
            subprocess.run(
                ['ffmpeg','-i',fileList[0],'-ss',str(ss),"tmpStart.wav"]
                ,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                ,check=True)
            # 끝파일
            subprocess.run(
                ['ffmpeg','-i',fileList[-1],'-to',str(to),"tmpEnd.wav"]
                ,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                ,check=True)
            #파일 리스트 임시생성
            tmpFileListTxt='tmpFileList.txt'
            with open(tmpFileListTxt,'w') as f:
                f.write("file tmpStart.wav\n")
                for file in fileList[1:-1]:
                    f.write(f"file '{file}'\n")
                f.write("file tmpEnd.wav\n")
            # 최종 파일 생성
            subprocess.run(
                ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', tmpFileListTxt
                  ,'-af', 'pan=2c|c0=c0|c1=c1', cutWav]
                ,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                , check=True)
                
            # 임시파일들 삭제
            os.remove("tmpStart.wav")
            os.remove("tmpEnd.wav")
            os.remove(tmpFileListTxt)

        ilkfs,mlkfs = getLoudness(cutWav)
    
        if not save:
            os.remove(cutWav)

        return ilkfs, mlkfs
    
    except : #중간에 프로그램 꺼졌을떄 남는 파일들 삭제
        if os.path.exists("tmpStart.wav"):
            os.remove("tmpStart.wav")
        if os.path.exists("tmpStart.wav"):
            os.remove("tmpStart.wav")
        if os.path.exists('tmpFileList.txt'):
            os.remove('tmpFileList.txt')
        if not save and os.path.exists(cutWav):
            os.remove(cutWav)

        print(traceback.format_exc())
        sys.exit(1)
    
if __name__ == "__main__":
    file = '/mnt/raid/audio/2024-09-07/CleanPGM_45_13-48-04.wav'
    data, rate = sf.read(file=file)
    data=data[:,0:2]
    meter=lkfs.Meter(rate)
    loudness,mlkfs = meter.integrated_loudness(data)
    print("original : ", loudness)
