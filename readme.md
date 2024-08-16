# Loudness Logging
Loudness Logging for SBS   

Used and Edited LKFS calc algorithm from [pyloudnrom](https://github.com/csteinmetz1/pyloudnorm)   

# 개요
### Input :
* 편성이 있는 디렉토리  
    * 편성파일 YYYYMMDD.xml
    * 프로그램 실행시 해당날짜 편성파일 자동 생성
    * scheduleRequest.py이용해 AIMS편성정보 따로 가져올 수도 있음
    * [SBS편성표 Example](./Ref/편성예시.xml)
* 오디오파일이 있는 디렉토리  
    * 오디오파일 YYYY-MM-DD_HH.00.00.wav
    * 한시간단위로 잘려진 레코딩 파일
    * recording/decklink_audio_rec.py 으로 SDI audio lossless recording 가능

*함수 Parameter : sdiMain(scheduleDir, audioDir, outputDir, chnlName, date="YYYY-MM-DD", outputAudioDir="")*

### Output :
* [outputDir]/[chnlName]_Loudness_Report_[date].xlsx   
    * columns : StartTime, EndTime, Duration, LKFS, ProgramName, PGMID 
* [outputDir]/mlkfs/[date]/[chnlName]_[PGM IDX}_[PGM Start Time].csv  
* (optional) [outputAudioDir]/[chnlName]_[PGM IDX]_[PGM Start Time].wav

Requirements :
* ffmpeg
* python module : openpyxl, ElementTree, soundfile, numpy
* for recording : gstreamer

## How to use
```shell
python main.py [option]
```
option : YYYY-MM-DD  , 없으면 default는 전일 편성 계산

---
### Scheduling
Ubuntu 서버 이용에 따라 crontab 이용해 main.py 코드 실행 스케줄링   
**편성이 06시(AM) 이후에 끝나는 날도 있기 때문에 전일 편성은 7시 이후 실행할 것**  
오전 8시 자동 실행 예시 : 
``` shell
0 8 * * * /home/logger/miniforge3/bin/python3 /home/logger/Documents/LoudnessLogging/main.py > /home/logger/Documents/LoudnessLogging/data/$(date +\%Y-\%m-\%d).log 2>&1
```

## 주요 구현 함수
### getLoudness.py
1. getLoudness (file)  
    wav파일 입력받아 ILKFS(float), MLKFS(float list) Return  
2. programLoudness(inputDir, startTime, endTime, correctionTime=0, save=True, outputDir="", fileName="tmpProgram")  
    오디오 파일 위치, 편성 정보를 입력받아 해당 편성의 ILKFS, MLKFS를 Return  
    편성 타임코드와 녹음의 타임코드가 정확히 맞지 않을때 correctionTime(seconds:float) 으로 보정 가능  
    프로그램 편성에 따라 자른 오디오 파일을 저장할 수 있음    

### main.py
1. sdiMain(scheduleDir,audioDir,outputDir,chnlName, date="YYYY-MM-DD", outputAudioDir="")  
    편성파일이 있는 디렉토리, 오디오파일이 있는 디렉토리를 입력받고 날짜에 따라 Loudness Report 생성  
    기본은 전일 편성 Loudness 계산


## Server Info
* CPU : i9-14900K
* CPU 쿨러 : 3RSYS Socoool RC1800 LITE (공냉)
* SSD : 삼성전자 990 Pro M.2 NVME 1T
* HDD :  WD BLUE 5640/256M (WD80EAAZ, 8TB) * 2ea
* 램 : SK하이닉스 DDR5-5600 (64GB(32Gx2))
* 그래픽 : NVIDIA T400 D6 4GB
* 마더보드 : ASUS PRIME Z790-P-CSM
* 파워 : 시소닉 NEW FOCUS GX-850 GOLD 풀모듈러 ATX3.0 
* 케이스 : 2MONS 4U D650 HD-28 워터쿨
* 확장보드 : Blackmagic Design DeckLink 8K Pro
* OS : Ubuntu 22.04 LTS

## Background
[과학기술정보통신부 KO-07.0114 디지털 방송 음성 레벨 운용 기준]에 따라 대한민국의 TV 프로그램은 평균음량을 -24LKFS으로 하며 운용상의 ±2dB이내 오차만 허용됨  
(LKFS 기준 : ITU-R BS.1770-3)    
지상파 방송국은 과기정통부에 프로그램별 Loudness를 로깅하고 제출할 의무가 있음    

이에따라 하루단위로 작일 편성표를 기준으로 Program별 Loudness를 측정하고 제출 가능한 문서형태로 값을 출력하는 프로그램 작성하게 됨    

### 관련법령
- 방송법 제70조의2(디지털 방송프로그램의 음량기준 등) 및 제98조(자료제출)
- 방송법 시행령 제68조(권한의 위임·위탁)
- 「디지털 텔레비전 방송프로그램 음량 등에 관한 기준」(과학기술정보통신부 고시)
- 「디지털 방송 음량 레벨 운용기준」(한국정보통신기술협회)
- 「디지털 텔레비전 방송프로그램 음량기준 등에 관한 업무지침」(중앙전파관리소 예규)