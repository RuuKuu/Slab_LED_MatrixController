from datetime import datetime

dt_now = datetime.now()
dt_now = datetime( 2020 , 1 , 1 , 0 , 3, 20 , 1230)

date_str = str(dt_now.month) + "/" + str(dt_now.day)

h = (" " + str(dt_now.hour))[-2:]
#スペースを頭に着けて最後から2文字背取得。1-9時の間も真ん中に時計が表示されるようにする考慮
time_str =  h + ":" + dt_now.strftime("%M")

print(date_str)
print(time_str)