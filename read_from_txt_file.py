########################################################################################################
#This file takes Arma 3 Be-Log data and attempts to retroactively determine the amount of users
#connected to an arma 3 server session using connects and disconnects to keep track of current users
########################################################################################################

import re
import os
import numpy as np
import datetime as dt
from dateutil import parser
import csv
from matplotlib import pyplot as plt

#Read through the working directory to discover all log files
#Return an array of all file names in the directory
def read_dir():
    filename_array = []
    for(files) in os.walk('Log_Reader/2020'):
        (val1, val2, val3) = files
        filename_array = val3
    return filename_array

#Import txt file into python to be read line by line
#Return the filename of the current working log file and an array of strings corresponding to each read line
def import_txt(file):
    directory = "Log_Reader/2020/" + file
    with open(directory, encoding='utf-8-sig') as f:
        array = []
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            line = line.replace('\ufeff', '')
            array.append(line.strip())
        filename = os.path.basename(f.name)
    return filename, array

#Edit the filename by removing excess characters
#Return the date extracted from the filename
def convert_filename_to_date(filename):
    filename = filename[3:]
    filename = filename[:len(filename)-4]
    date = filename
    return date

#Write a given array to an external csv file
def write_to_csv(array):
    rows = array
    with open('connections_data.csv', mode='w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['time', 'connected_Users'])
        for row in rows:
            writer.writerow(row)
    return

#Append connected_Users array to CSV file called: connections_data.csv
def append_csv(array):
    rows = array
    with open('connections_data.csv', mode='a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        #writer.writerow(['time', 'connected_Users'])
        for row in rows:
            writer.writerow(row)

def write_connect_disconnect_array_to_csv(combined_connect_disconnect_array):
    rows = combined_connect_disconnect_array
    with open('connect_disconect_array.csv', mode='a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        #writer.writerow(['time', 'connected_Users'])
        for row in rows:
            writer.writerow(row)
    return

def write_guids_to_csv(guid_tuple_array):
    rows = guid_tuple_array
    with open('guid_tuple_array.csv', mode='a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        #writer.writerow(['time', 'connected_Users'])
        for row in rows:
            writer.writerow(row)
    return

#Add an unexpected restart to the connection data
#Return array of unexpected restarts
def add_unexpected_restart(string, date):
    array = []
    string = string[:8]
    datetime = date + " " +string
    time = parser.parse(datetime)
    tuple = (time, "GlobalUser(Unexpected Disconnect)", "unexpected")
    array.append(tuple)
    #print("Unexpected restart at:", time)
    return array

#Check if a restart occurs outside of its designated time
#Return TRUE if restart falls within the acceptable bounds
#Return FALSE if restart falls outside the acceptable bounds
def check_restart(string):
    timeconst1 = parser.parse("04:00:00")
    timeconst2 = parser.parse("04:10:00")
    timeconst3 = parser.parse("10:00:00")
    timeconst4 = parser.parse("10:10:00")
    timeconst5 = parser.parse("14:00:00")
    timeconst6 = parser.parse("14:10:00")
    timeconst7 = parser.parse("18:00:00")
    timeconst8 = parser.parse("18:10:00")
    time = string[:8]
    time = parser.parse(time)
    if(timeconst1 < time < timeconst2):
        return True
    elif(timeconst3 < time < timeconst4):
        return True
    elif(timeconst5 < time < timeconst6):
        return True
    elif(timeconst7 < time < timeconst8):
        return True
    else:
        return False

#Loop through array of strings corresponding to the input data to separate connections and disconnections
#Also checks if users got kicked
#Also checks if unexpected restarts occur
#Return connect_array: array of all connecting clients 
#Return disconnect_array: array of all disconnecting clients
#Return guid_array: array of all clients by name and GUID
#Return unexpected_restart_array: array of all unexpected restarts
def extract_connections(array, date):
    substring_A = "disconnected"
    substring_B = " connected"
    substring_C = "BE Master"
    substring_D = "BE GUID"
    substring_E = "has been kicked by BattlEye"
    substring_F = "Starting plugin : ConnectionLimiter"
    substring_G = "GUID"
    disconnect_array = []
    connect_array = []
    guid_array = []
    battleye_array = []
    unexpected_restart_array = []
    i = 1
    while(i < len(array)):
        string = array[i]
        if string.endswith(substring_A) == True:
            if substring_C in string:
                i = i + 1
            else:
                disconnect_array.append(array[i])
                i = i + 1
        elif string.endswith(substring_B) == True:
            if substring_C in string:
                i = i + 1 
            else:
                connect_array.append(array[i])
                i = i + 1
        elif substring_D in string:
            if "Verified GUID" in string:
                i = i + 1
            else:
                guid_array.append(array[i])
                i = i + 1
        elif substring_G in string:
            if "Verified GUID" in string:
                i = i + 1
            else:
                guid_array.append(array[i])
                i = i + 1
        elif substring_E in string:
            battleye_array.append(array[i])
            i = i + 1
        elif substring_F in string:
            if(check_restart(array[i]) == True):
                i = i + 1
            else:
                unexpected_restart_array = add_unexpected_restart(array[i], date)
                i = i + 1
        else:
            i = i + 1
    return connect_array, disconnect_array, guid_array, battleye_array, unexpected_restart_array

#Generate tuple in form (GUID, Name) from guid_array
#Source string looks like: "13:46:13 : Player #21 AZ - BE GUID: 76cc91bb5e29e1f8948587820ac2b9ee"
#Source string looks like: "00:02:14 : Player #54 Ethan Johnson - GUID: c710750d3ed6e15e3746fd87f3ff66c8"
#REGEX  reg = re.search(pattern= '\w{32}', string=string).group()
#reg1 = re.match("#[0-9]{1,3}", string).span()
#        (start, end) = reg1
#        string = string[end+1:]
def guid_tuple_regex(guid_array):      #guid_array                                                                                    
    guid_tuple_array = []
    substring_A = "BE GUID"
    for x in range(len(guid_array)):                                                                                          
        string = guid_array[x]
        string = str(string)
        #string = "00:00:19 : Player #11 Super Svein - GUID: afa90ec652d3f7ae1aee36da285d265a"
        guid = re.search(pattern= '\\w{32}', string=string)
        assert guid is not None
        guid = guid.group()
        string = string[18:]
        reg1 = re.match("#[0-9]{1,3}", string)
        assert reg1 is not None
        reg1 = reg1.span()
        (start, end) = reg1
        string = string[end+1:]
        if substring_A in string:
            string = string[:len(string)-44]
            tuple = (guid, string)
        else:
            string = string[:len(string)-41]
            tuple = (guid, string)
        guid_tuple_array.append(tuple)
    guid_tuple_array = list(set(guid_tuple_array))
    return guid_tuple_array

#Generate tuple in form of (Time, Name, ConnectionStatus)
#Source string looks like: "00:50:31 : Player #63 |BrPlay| BlacK.762™ (177.137.237.127:2304) connected"
def connected_tuple_regex(connect_array, date):
    connected_tuple_array = []
    i = 1
    while(i < len(connect_array)):
        string = connect_array[i]
        time = string[:9]
        string = string[18:]
        size = len(string)
        string = string[:size-10]

        reg1 = re.match("#[0-9]{1,3}", string)
        assert reg1 is not None
        reg1 = reg1.span()
        (start, end) = reg1
        end = int(end)
        string = string[end+1:]

        datetime = date + " " + time
        datetime = parser.parse(datetime)

        reg2 = re.search(pattern="(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}):(\\d{1,5})", string=string)
        assert reg2 is not None
        reg2 = reg2.group()
        regex_size = len(reg2) + 3
        size = len(string)
        string = string[:size - regex_size]
        tuple = (datetime, string, "connected")
        connected_tuple_array.append(tuple)
        i = i + 1
    return connected_tuple_array

#Generate tuple in form (Time, Name, ConnectionStatus)
#Source string looks like: "00:26:00 : Player #47 mick disconnected"
def disconnected_tuple_regex(disconnect_array, date):
    disconnected_tuple_array = []
    i = 1
    while(i < len(disconnect_array)):
        string = disconnect_array[i]
        time = string[:8]
        string = string[18:]
        string = string[:len(string)-13]

        reg1 = re.match("#[0-9]{1,3}", string)
        assert reg1 is not None
        reg1 = reg1.span()
        (start, end) = reg1
        end = int(end)
        string = string[end+1:]

        datetime = date + " " + time
        datetime = parser.parse(datetime)

        tuple = (datetime, string, "disconnected")
        disconnected_tuple_array.append(tuple)
        i = i + 1
    return disconnected_tuple_array

#source strings look like:
#22:59:31 : Player #241 frapunzel (3130e2dbcfed02e9015d6bd19f489f2b) has been kicked by BattlEye: Game restart required
def regex_battleye_disconnects(batteleye_array, date):
    array = []
    for string in batteleye_array:
        test = True
        time = string[:8]       #Extract time
        datetime = date + " " + time
        datetime = parser.parse(datetime)
        string = string[19:]    #241 frapunzel (3130e2dbcfed02e9015d6bd19f489f2b) has been kicked by BattlEye: Game restart required
        #print(string)
        try:
            reg = re.search(pattern= '\\w{32}', string=string)
            assert reg is not None
            reg = reg.group()
        except:
            print("An error occured in finding the GUID")
            test = False
        if(test != False):
            reg = re.search(pattern= '\\w{32}', string=string)
            assert reg is not None
            reg = reg.group()
            guid = reg              #Extract GUID
            status = "disconnected(BE)"
            tuple = (datetime, guid, status)
            #print(tuple)
            array.append(tuple)
        else:
            continue
    return array

#Combine the GUID and Connection Arrays by identical GUID
#Return array of GUID connections
def combine_GUID_Connection_Tuples(guid_tuple_array, connected_tuple_array):
    i = 1
    guid_connect_array = []
    while(i < len(connected_tuple_array)):
        tuple1 = connected_tuple_array[i]
        (time, name1, status) = tuple1
        j = 1
        while(j < len(guid_tuple_array)):
            tuple2 = guid_tuple_array[j]
            (guid, name2) = tuple2
            if (name2 == name1):
                new_tuple = (time, guid, status)
                guid_connect_array.append(new_tuple)
                break
            else:
                j = j + 1
        i = i + 1
    return guid_connect_array

#Combine the GUID and Disconnection Arrays by identical GUID
#Return array of GUID disconnections
def combine_GUID_Disconnection_Tuples(guid_tuple_array, disconnected_tuple_array):
    i = 1
    guid_disconnect_array = []
    while(i < len(disconnected_tuple_array)):
        tuple1 = disconnected_tuple_array[i]
        (time, name1, status) = tuple1
        j = 1
        while(j < len(guid_tuple_array)):
            tuple2 = guid_tuple_array[j]
            (guid, name2) = tuple2
            if (name2 == name1):
                new_tuple = (time, guid, status)
                guid_disconnect_array.append(new_tuple)
                break
            else:
                j = j + 1
        i = i + 1
    return guid_disconnect_array

#Not working
#Calculate time online
def find_timedelta(combined_connect_disconnect_array, guid_tuple_array):
    array = []
    i = 1
    while(i < len(guid_tuple_array)):
        user_array = []
        tuple1 = guid_tuple_array[i]
        (guid1, name) = tuple1
        j = 1
        while(j < len(combined_connect_disconnect_array)):
            tuple2 = combined_connect_disconnect_array[j]
            (time, guid2, status) = tuple2
            if(guid1 == guid2):
                user_array.append(tuple2)
                j = j + 1
            else:
                j = j + 1
        array.append(user_array)
        i = i + 1
    size_array = len(array)
    write_to_csv(array)
    return array, size_array

#Add global disconnects
#Return array of global disconnects
def add_global_disconnects(date):
    global_disconnects_array = []
    restart1 = parser.parse(date + " 04:00:00")
    restart2 = parser.parse(date + " 10:00:00")
    restart3 = parser.parse(date + " 14:00:00")
    restart4 = parser.parse(date + " 18:00:00")
    restart_array = [restart1, restart2, restart3, restart4]
    for x in restart_array:
        tuple = (x, "GlobalUser", "DISCONNECTED")
        global_disconnects_array.append(tuple)
    return global_disconnects_array

#Find currently active users
#Return the number of active users at a point in time
def find_Online_Users(combined_connect_disconnect_array):
    session_1 = []          #00:00 till 04:00
    session_2 = []          #04:00 till 10:00
    session_3 = []          #10:00 till 14:00
    session_4 = []          #14:00 till 18:00
    session_5 = []          #18:00 till 00:00
    session_arrays = [session_1, session_2, session_3, session_4, session_5]
    connected_users_array = []
    polling_array = []
    i = 0
    for x in combined_connect_disconnect_array:
        (time, guid, status) = x
        if(guid != "GlobalUser"):
            session_arrays[i].append(x)
        else:
            i = i + 1
    i = 0
    average_users_session = []
    while(i <= 4):
        connected_users = 0
        array = session_arrays[i]
        total_connected_users = 0
        array_length = len(array)
        #print("Session is Session:", i + 1)
        for x in array:
            (time, guid, status) = x
            if(connected_users>70):
                print("Connected Users exceeds the limit of 70")
            if(status == "unexpected"):
                connected_users = 0
            if(status == "connected"):
                connected_users = connected_users + 1
                total_connected_users = total_connected_users + connected_users
                tuple = (time, connected_users)
                connected_users_array.append(tuple)
                #print(time, "Currently connected users are:", connected_users)
            if(status == "disconnected"):
                    if(connected_users == 0):
                        continue
                    elif(connected_users != 0):
                        connected_users = connected_users - 1
                        total_connected_users = total_connected_users + connected_users
                        tuple = (time, connected_users)
                        connected_users_array.append(tuple)
                        #print(time, "Currently connected users are:", connected_users)
            if(status == "disconnected(BE)"):
                connected_users = connected_users - 1
                total_connected_users = total_connected_users + connected_users
                tuple = (time, connected_users)
                connected_users_array.append(tuple)
                #print(time, "Currently connected users are:", connected_users)
            if(guid == "Polling"):
                tuple = (time, connected_users)
                polling_array.append(tuple)
            if(connected_users<0):
                print("Connected Users cannot be negative")
        i = i + 1
        average = total_connected_users/array_length
        average = round(average)
        average_users_session.append(average)
    return connected_users_array, polling_array, average_users_session

def fixed_time_intervall_arrays(date):
    fixed_time_intervall_arrays = []
    time_arrays = []
    start = parser.parse(date + " 00:00:00")
    step =  dt.timedelta(minutes=15)
    next_day_delta = dt.timedelta(days=1)
    next_day = start + next_day_delta
    end = parser.parse(date + " 23:59:59")
    time_arrays.append(start)
    while((start + step) < end):
        time_arrays.append(start + step)
        start = start + step
    time_arrays.append(next_day)
    for x in time_arrays:
        tuple = (x, "Polling", "no status")
        fixed_time_intervall_arrays.append(tuple)
    return fixed_time_intervall_arrays

def calculate_average_user_count(polling):
    total_users = 0
    for x in polling:
        (time, user_count) = x
        total_users = total_users + user_count
    average_users = total_users/ len(polling)
    average_users = round(average_users)
    #print("Length is:", len(polling))
    return average_users

def get_unique_connectiondata(combined_connect_disconnect_array):
    i = 1
    unique_array = []
    unique_GUID = "8ae3ea893f010efa869c244c9d514ce4"            #test
    while(i < len(combined_connect_disconnect_array)):
        (datetime, guid, status) = combined_connect_disconnect_array[i]
        if(unique_GUID == guid):
            unique_array.append(combined_connect_disconnect_array[i])
            i = i + 1
        else:
            i = i + 1
    return unique_array

def parse_connection_time(user_unique_connections):
    i = 0
    timedelta_array = []
    while(i < len(user_unique_connections)):
        (datetime1, guid1, status1) = user_unique_connections[i]
        if(status1 == "connected"):
            (datetime2, guid2, status2) = user_unique_connections[i+1]
            if (status2 == "disconnected"):
                timedelta = datetime2 - datetime1
                timedelta_array.append(timedelta)
                i = i + 2
        else:
            i = i + 1
    return timedelta_array

def total_online_time_user(timedelta_array):
    total_online_time = sum(timedelta_array, dt.timedelta())
    return total_online_time

def main():
    filename_array = read_dir()                         #Find all log files in folder and convert to strings
    filename_array_size = len(filename_array)
    print(filename_array_size)
    i = 1
    huge_array = []
    while(i <= 1):
        array = []
        file = filename_array[i-1]      #Select file here
        print(file)
        date = convert_filename_to_date(file)
        file_name, array = import_txt(file)
        print("Size of input array is:", len(array))
        connect_array, disconnect_array, guid_array, battleye_array, unexpected_restart_array = extract_connections(array, date)
        print("Size of connect_array is:", len(connect_array))
        print("Size of disconnect_array is:", len(disconnect_array))
        print("Size of guid_array is:", len(guid_array))
        print("Size of battleye_array is:", len(battleye_array))
        print("Size of unexpected_restart_array is:", len(unexpected_restart_array))                        
        be_disconnects = regex_battleye_disconnects(battleye_array, date)
        guid_tuple_array = guid_tuple_regex(guid_array)                                                                                       #(GUID, Name)
        connected_tuple_array = connected_tuple_regex(connect_array, date)                                                                    #(Time, Name, ConnectionStatus)
        disconnected_tuple_array = disconnected_tuple_regex(disconnect_array, date)                                                           #(Time, Name, ConnectionStatus)
        guid_connect_array = combine_GUID_Connection_Tuples(guid_tuple_array, connected_tuple_array)                                          #(Time, GUID, ConnectionStatus=connected)
        guid_disconnect_array = combine_GUID_Disconnection_Tuples(guid_tuple_array, disconnected_tuple_array)                                 #(Time, GUID, ConnectionStatus=disconnected)
        combined_connect_disconnect_array = guid_connect_array + guid_disconnect_array
        global_disconnects = add_global_disconnects(date)
        polling_array = fixed_time_intervall_arrays(date)
        combined_connect_disconnect_array = combined_connect_disconnect_array + global_disconnects + be_disconnects + unexpected_restart_array + polling_array
        sorted_array = sorted(combined_connect_disconnect_array, key=lambda tup: tup[0])
        combined_connect_disconnect_array = sorted_array
        connected_users_array, polling, average_users_session = find_Online_Users(combined_connect_disconnect_array)
        user_unique_connections = get_unique_connectiondata(combined_connect_disconnect_array)
        unique_user_connection_time = parse_connection_time(user_unique_connections)
        total_online = total_online_time_user(unique_user_connection_time)
        average_user_count = calculate_average_user_count(polling)
        #write_connect_disconnect_array_to_csv(combined_connect_disconnect_array)
        #for x in guid_tuple_array:
        #    print(x)
        #write_guids_to_csv(guid_tuple_array)
        i = i + 1
    #sorted_unique_guid_array = sorted(huge_array, key= lambda tup: tup[0])
    #print(guid_tuple_array)


    #Plotting section
    date = str(date)
    graph_label = "Online users on: " + date
    x_labels = [val[0] for val in polling]  # type: ignore
    y_labels = [val[1] for val in polling]  # type: ignore
    plt.title(graph_label)
    plt.plot(x_labels, y_labels)
    plt.grid()
    session1 = "Average users: " + str(average_users_session[0])
    session2 = "Average users: " + str(average_users_session[1])
    session3 = "Average users: " + str(average_users_session[2])
    session4 = "Average users: " + str(average_users_session[3])
    plt.figtext(.23, .8, session1)
    plt.figtext(.415, .8, session2)
    plt.figtext(.55, .8, session3)
    plt.figtext(.7, .8, session4)
    restarts = []
    for x in global_disconnects:
        (time, user, status) = x
        restarts.append(time)
    plt.vlines(restarts, ymin = 0, ymax = 70, colors = 'red')
    plt.show()

main()

#TODO
#Generate array that conatins all disconnects from certain GUID per year
#Add global disconnects if disconnects missing at end of each session
#Figure out how to deal wih overlapping days and sessions
#Find timedelta between user connect and disconnect and add to global time.
#Generate usage time for each session
#Generate time per session and time per day per year