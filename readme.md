# Loudness Logging
Loudness Logging for SBS   

## 개요
Input :
* 작일 편성표 : .xml (SBS 편성표 형식 그대로)
* 작일 방송분 : .ts or .mp4 (아카이빙 자료 이용)

Output :
* excel file : Loudness_Report_[date].xlsx   
this includes : StartTime, EndTime, Duration, LKFS, ProgramName, PGMID   

Requirements :
* openpyxl, ElementTree, soundfile


## Background
법령 [과학기술정보통신부 KO-07.0114 디지털 방송 음성 레벨 운용 기준]에 따라 대한민국의 TV 프로그램은 평균음량을 -24LKFS으로 하며 운용상의 ±2dB이내 오차만 허용됌  
(LKFS 기준 : ITU-R BS.1770-3)    
지상파 방송국은 과기정통부에 프로그램별 Loudness를 로깅하고 제출할 의무가 있음

이에따라 하루단위로 작일 편성표를 기준으로 Program별 Loudness를 측정하고 제출 가능한 문서형태로 값을 출력하는 프로그램 작성하게 됌
       
Used and Edited LKFS calc algorithm from [pyloudnrom](https://github.com/csteinmetz1/pyloudnorm)    
    
    