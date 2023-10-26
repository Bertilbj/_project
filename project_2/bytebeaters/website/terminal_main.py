"""
Terminal program til at registere fremmøde i databasen.
"""

from datetime import datetime
from time import sleep

import DFRobot_RGBLCD1602
import RPi.GPIO as GPIO
from class_manager import Logging, Student, Terminal
from mfrc522 import MFRC522, SimpleMFRC522


class MyReader(SimpleMFRC522):
    """
    Overskriver SimpleMFRC522 klassen, da den ikke angiver hvor pin_rst er.
    Dette er nødvendigt for at kunne bruge den korrekt med SPI.
    I MFRC522 klassen er pin_rst sat til 22, hvilket ikke er korrekt for os.
    I tilfælde af en ny Terminal bruger en anden bus er device også defineret.
    """

    def __init__(self):
        self.READER = MFRC522(device=0, pin_rst=13)


if __name__ == "__main__":
    lcd = DFRobot_RGBLCD1602.LCD()
    reader = MyReader()

    # ID på terminalen, skal være forskellig på hver enkelt Terminal.
    # Statisk værdi, derfor skrevet med stort.
    TERMINAL_ID = 1
    THIS_TERM = Terminal.get_name(TERMINAL_ID)

    def succes(card_id):
        time = datetime.now().strftime('%H:%M')
        date = datetime.now().strftime('%d/%m/%Y')
        # Henter navnet på den studerende, der har scannet sit kort.
        name = Student.get_name(card_id)
        lcd.set_RGB(0, 255, 0)
        lcd.print_out(f"{name}, {Student.get_team(card_id)}")
        # Gør klar til at skrive på den næste linje.
        lcd.set_cursor(0, 1)
        lcd.print_out(
            f"{THIS_TERM}, {time} - {date}")
        sleep(0.5)
        # Scroller teksten på displayet
        for _ in range(0, len(name)-5):
            lcd.scroll_display_left()
            sleep(0.30)
        sleep(1.5)

    def fail(card_id):
        time = datetime.now().strftime('%H:%M')
        date = datetime.now().strftime('%d/%m/%Y')
        # Hvis kortet ikke er i databasen.
        lcd.set_RGB(255, 0, 0)
        lcd.print_out(f"{card_id} findes ikke i systemet.")
        # Gør klar til at skrive på den næste linje.
        lcd.set_cursor(0, 1)
        lcd.print_out(
            f"{THIS_TERM}, {time} - {date}")
        sleep(0.5)
        # Scroller teksten på displayet
        for _ in range(0, 20):
            lcd.scroll_display_left()
            sleep(0.30)
        sleep(1.5)

    while True:
        try:
            card_id = reader.read()[0]

            # Når et kort scannes, og det er i databasen.
            if card_id in Student.get_card_ids():
                succes(card_id)
                # Logger fremmødet i databasen.
                Terminal.register_attendance(
                    TERMINAL_ID, card_id, Terminal.get_team(TERMINAL_ID))
                Logging.success_login_terminal(card_id, THIS_TERM,
                                               Student.get_id(card_id))
            else:
                fail(card_id)
                # Logger forsøget i databasen.
                Logging.failed_login_terminal(card_id, THIS_TERM)

            # Nulstiller displayet. Gør klar til næste scanning.
            lcd._begin(2, 16)

        # Stopper programmet ved CTRL+C
        except KeyboardInterrupt:
            # Slukker displayet korrekt og rydder op på GPIO pins. Lukker programemt.
            print("Cleaning up!")
            lcd.no_display()
            lcd.close_backlight()
            GPIO.cleanup()
            break
