# Loudness Logging
Loudness Logging for SBS   

Used and Edited LKFS calc algorithm from [pyloudnrom](https://github.com/csteinmetz1/pyloudnorm)   
    
## 개요
Input :
* 작일 편성표 : .xml (SBS 편성표 형식 그대로)
* 작일 방송분 : .ts (winTV + TV Headend 이용 RF 레코딩)

Output :
* excel file : Loudness_Report_[date].xlsx   
this includes : StartTime, EndTime, Duration, LKFS, ProgramName, PGMID   

Requirements :
* openpyxl, ElementTree, soundfile

### Scheduling
Ubuntu 서버 이용에 따라 crontab 이용해 main.py 코드 실행 스케줄링    
오전 8시 자동 실행 예시 : 
```
0 8 * * * /home/logger/miniforge3/bin/python3 /home/logger/Documents/LoudnessLogging/main.py > /home/logger/Documents/LoudnessLogging/data/$(date +\%Y-\%m-\%d).log 2>&1
```

### Recording Info (Not Included in this code)
TV Headend Recording Timer :    
Start Time 04:00 End Time 03:30    
\+ post padding 4 hrs    
=> total 04:00 ~ 07:30(N) recording    
30 min at the end is considered margin   

## Background
법령 [과학기술정보통신부 KO-07.0114 디지털 방송 음성 레벨 운용 기준]에 따라 대한민국의 TV 프로그램은 평균음량을 -24LKFS으로 하며 운용상의 ±2dB이내 오차만 허용됨  
(LKFS 기준 : ITU-R BS.1770-3)    
지상파 방송국은 과기정통부에 프로그램별 Loudness를 로깅하고 제출할 의무가 있음    

이에따라 하루단위로 작일 편성표를 기준으로 Program별 Loudness를 측정하고 제출 가능한 문서형태로 값을 출력하는 프로그램 작성하게 됨    