import os
import datetime
import shutil

def oldClearing(path, days):
    # 현재 날짜
    current_time = datetime.datetime.now()
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
    oldClearing('D:/audio',3)
    # 레코딩 삭제
    oldClearing('D:/recording/SBS_HD',100)

if __name__ == '__main__':
    print('N/A')