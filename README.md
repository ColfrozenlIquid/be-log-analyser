
# Arma 3 Server Log Reader

Two simple scripts to convert raw Battleye-Log Data from Arma 3 game servers into some usable data.
This project started out as an attempt to find out unique users online time across multiple years of the servers online time. Arma 3 Servers do not log each users online time as is, so a script was designed to attempt to retroactively calculate this.

This issue could have been avoided by adding to the functions that feed the database created by extDB3 (https://github.com/SteezCram/extDB3). However, this would not allow for generating data retroactively.

- Script "read_from_text_file.py" attempts to convert input BE-Log Data into a usable CSV file format
- Script "get_user_online_time.py" uses the previously generated CSV files to determine a give GUIDs online time according to their individual connect and disconnect times




## Screenshots

Sample Log Data
![App Screenshot](https://i.imgur.com/OP8uBsW.png)

Sample Result
![App Screenshot](https://i.imgur.com/sIyaFlY.png)
The returned result attempts to recreate the user count on the server for each of the alloted server uptimes. Red lines indicate a sheduled server restart.


## Current plans/issues
- (-) Unplanned server restarts/crashes are unhandled



