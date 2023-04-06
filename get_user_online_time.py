import datetime
import csv
from dateutil import parser

def import_csv(user_input):
    input_guid = user_input
    unique_user_connections = []
    file_array = ["connect_disconect_array_2019.csv", "connect_disconect_array_2020.csv",\
        "connect_disconect_array_2021.csv", "connect_disconect_array_2022.csv"]
    for x in file_array:
            with open(x, newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        (time, guid, status) = row
                        if(guid == input_guid):
                            unique_user_connections.append(row)
                        if(guid == "GlobalUser"):
                            unique_user_connections.append(row)
                        if(guid == "GlobalUser(Unexpected Disconnect)"):
                            unique_user_connections.append(row)
                        else:
                            continue
    return unique_user_connections

def determine_online_time(unique_user_connections):
    i = 0
    timedelta_array = []
    while(i < len(unique_user_connections)):
        if(i+2 > len(unique_user_connections)):
            break
        (time1, guid1, status1) = unique_user_connections[i]
        if(status1 == "connected"):
            (time2, guid2, status2) = unique_user_connections[i+1]
            if(status2 == "disconnected" or status2 == "DISCONNECTED" or status2 == "unexpected" or status2 == "disconnected(BE)"):
                time1 = parser.parse(time1)
                time2 = parser.parse(time2)
                timedelta = time2 - time1
                timedelta_array.append(timedelta)
                i = i + 2
            else:
                i = i + 1
        else:
            i = i + 1
    return timedelta_array

def calculate_total_online_time_annually(timedelta_array):
    total_online_time = sum(timedelta_array, datetime.timedelta())
    return total_online_time

def main():
    print("Input user GUID:")
    user_input = input()
    unique_user_connections = import_csv(user_input)
    time = determine_online_time(unique_user_connections)
    total_time = calculate_total_online_time_annually(time)
    print(total_time)
    return

main()