import pyloudnorm as pyln
import soundfile as sf
import subprocess
import os

def getLoudness(file):
    data, rate = sf.read(file) #data.shape : (길이, 채널수) 
    meter = pyln.Meter(rate)
    loudness = meter.integrated_loudness(data)
    return loudness

def splitAndLoud(file_path,start_time,duration):
    subprocess.run(['ffmpeg','-i',file_path,'-ss',str(start_time),'-t',str(duration),'-c','copy',"./data/tmpWav.wav"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    lufs = getLoudness("./data/tmpWav.wav")
    os.remove("./data/tmpWav.wav")
    return lufs
