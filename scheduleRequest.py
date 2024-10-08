import requests
from datetime import datetime, timedelta
from pprint import pprint
from xml.etree.ElementTree import Element, SubElement, ElementTree
import math, os

def scheduleRequest(savingPath,date="YYYY-MM-DD"):
    #date 입력값이 없으면 하루 전 편성 요청이 default
    if date=="YYYY-MM-DD":
        today = datetime.now()
        date = today - timedelta(days=1)
        date = date.strftime("%Y-%m-%d")
    target = f"http://10.110.21.31/cms/api/frmtn/dailyInfo.json?date={date}&UHDSchedule=False"

    response = requests.get(target)
    response_json = response.json()
    items = response_json["items"]
    filename = date.replace("-", "") + ".xml"

    root = Element("EventList")
    for index, item in enumerate(items):
        EventInfo = SubElement(root, "EventInfo")
        SubElement(EventInfo, "EventIndex").text = item["EventIndex"]
        startDate = item["StartTime"].split(" ")[0].split("-")
        OnAirDate = startDate[2] + "/" + startDate[1] + "/" + startDate[0]
        SubElement(EventInfo, "OnAirDate").text = OnAirDate
        SubElement(EventInfo, "StartTime").text = item["StartTime"].split(" ")[1] + ":00"
        duartion_in_seconds = int(item["Duration"])
        duration_hours = math.floor(duartion_in_seconds / 3600)
        duration_minutes = math.floor((duartion_in_seconds - 3600 * duration_hours) / 60)
        duration_seconds = duartion_in_seconds % 60
        Duration = f"{format(duration_hours, '02')}:{format(duration_minutes, '02')}:{format(duration_seconds, '02')}:00"
        SubElement(EventInfo, "Duration").text = Duration
        SubElement(EventInfo, "PGMID").text = item["ProgramID"]
        SubElement(EventInfo, "EventTitle").text = item["ProgramItemName"]
        SubElement(EventInfo,"DescriptiveVideoService").text=item["DescriptiveVideoService"]

    tree = ElementTree(root)
    tree.write(os.path.join(savingPath, filename), encoding="utf8")

if __name__ == "__main__" : 
    scheduleRequest("/mnt/raid/schedule")