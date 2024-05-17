import lkfs
import soundfile as sf
import subprocess
import os

def getLoudness(file):
    data, rate = sf.read(file) #data.shape : (길이, 채널수) 
    meter = lkfs.Meter(rate)
    loudness, mlkfs = meter.integrated_loudness(data)
    return loudness, mlkfs

def splitAndLoud(file_path,start_time,duration):
    fileName="./data/"+str(start_time)+"tmpWav.wav"
    #subprocess.run(['ffmpeg','-i',file_path,'-ss',str(start_time),'-t',str(duration),'-c','copy',"./data/"+str(start_time)+"tmpWav.wav"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    lufs, mlkfs = getLoudness(fileName)
    #os.remove("./data/"+str(start_time)+"tmpWav.wav")
    return lufs, mlkfs
