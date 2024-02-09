import time
import threading

def hello():
    print ("hello, world")
    time.sleep(2)

t = threading.Timer(3.0, hello)
t.start()

var = 'something'
if var == 'something':
    t.cancel()
