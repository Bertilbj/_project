#!/usr/bin/env python

from time import sleep

import RPi.GPIO as G
from rfi.old.LCD_new import LCD
from mfrc522 import SimpleMFRC522

G.setmode(G.BCM)
LED_RED = 21
LED_GREEN = 20
BUZZER = 12


G.setup([LED_RED, LED_GREEN, BUZZER], G.OUT)
buz = G.PWM(BUZZER, 1500)
data_pins = [23, 24, 27, 22, 5, 6, 16, 26]

reader = SimpleMFRC522()
screen = LCD(rs_pin=17, e_pin=4, d_pins=data_pins, n_lines=LCD.LINES_FOUR,
             font=LCD.FONT_5X8, n_cols=16, line_addresses=[0x00, 0x40, 0x10, 0x50])
screen.display_on_off(1, 0, 0)
for _ in range(2):
    try:
        id, text = reader.read()
        print(id)
        print(f"*{text.strip()}*")
        if id == 275288510832:
            G.output(LED_GREEN, G.HIGH)
            screen.write_string(f"ID: {str(id)}")
            screen.cursor.set_cursor_pos(1, 0)
            screen.write_string(text.strip())
            print(text)
            buz.start(90)
            sleep(0.4)
            buz.stop()
        else:
            G.output(LED_RED, G.HIGH)
            screen.write_string("Access")
            screen.cursor.set_cursor_pos(1, 0)
            screen.write_string("Denied")
            screen.cursor.set_cursor_pos(2, 0)
            screen.write_string("Loser")
            screen.cursor.set_cursor_pos(3, 0)
            screen.write_string("Try Again !")
            buz.start(90)
            sleep(0.2)
            buz.stop()
            sleep(0.2)
            buz.start(90)
            sleep(0.2)
            buz.stop()
        sleep(3)

    finally:
        G.output(LED_RED, G.LOW)
        G.output(LED_GREEN, G.LOW)
        screen.clear_display()
G.cleanup()
