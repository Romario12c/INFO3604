import RPi.GPIO as GPIO
import time
from RxTx import RxTx
from DataRW import DataRW
import keys
rxtx = RxTx()
data = DataRW()
channel = 21
#GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

def callback(channel):
    if GPIO.input(channel):
        print("hi")
        titles = data.getTitles()
        titles.reverse()
        for title in titles:
            c1, c2, c3, c4, c5, c6 = data.getOnParameters(title)
            rxtx.txCode(c1, c2, c3, c4, c5, c6)
            time.sleep(5)
    else:
        print("bye")
        titles = data.getTitles()
        titles.reverse()
        for title in titles:
            c1, c2, c3, c4, c5, c6 = data.getOffParameters(title)
            rxtx.txCode(c1, c2, c3, c4, c5, c6)
            time.sleep(5)
        print("Out of water")
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime = 300)
GPIO.add_event_callback(channel, callback)

while True:
    time.sleep(1)