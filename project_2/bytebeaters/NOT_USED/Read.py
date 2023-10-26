#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep
GPIO.setmode(GPIO.BCM)
LED_RED = 27
LED_GREEN = 22
GPIO.setup([LED_RED, LED_GREEN], GPIO.OUT)
reader = SimpleMFRC522()

try:
    id, text = reader.read()
    print(id)
    print(f"*{text.strip()}*")
    #print(type(text))
    if text.strip() == "hej":
        GPIO.output(LED_GREEN, GPIO.HIGH)
        print(text)
    else:
        GPIO.output(LED_RED, GPIO.HIGH)
    sleep(3)
    GPIO.output(LED_RED, GPIO.LOW)
    GPIO.output(LED_GREEN, GPIO.LOW)


finally:
    GPIO.cleanup()
