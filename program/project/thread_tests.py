import threading
from random import randint
from time import sleep


def f():
    while True:
        print(randint(0, 9))

t = threading.Thread(target=f, name = "Test")
t.setDaemon(True)
t.start()

print("Starting")
sleep(2)
print("Ending")