from multiprocessing.connection import answer_challenge
import serial

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=2)
c = ser.readline()
ser.close()

ans = c.decode("utf-8")

anslist = ans.split()

if anslist[0] == "Data:":
    Temp = anslist[2]
    Humidity = anslist[4]
    Heatindex = anslist[6]

elif anslist[0] != "Data:":
    Temp = "センサ"
    Humidity = "接続"
    Heatindex = "異常" 

print(ans)

print(Temp)
print(Humidity)
print(Heatindex)