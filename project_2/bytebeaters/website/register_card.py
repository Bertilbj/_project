"""
Terminal program til at registrere kort i databasen.
"""
from time import sleep

import DFRobot_RGBLCD1602
import RPi.GPIO as GPIO
from class_manager import Card
from terminal_main import MyReader

if __name__ == "__main__":
    lcd = DFRobot_RGBLCD1602.LCD()
    reader = MyReader()

    while True:
        try:
            card_id = reader.read()[0]
            # Hvis et gyldigt kort scannes, og det ikke er i databasen.
            if not card_id in Card.get_all_card_ids() and len(str(card_id)) == 12:
                Card(card_id)
                lcd.set_RGB(0, 255, 0)
                lcd.print_out(f"{card_id}")
                lcd.set_cursor(0, 1)
                lcd.print_out("Registeret")
            # Hvis et ugyldigt kort scannes. (Ikke 12 cifre) Feks. NFC fra en mobiltelefon
            elif len(str(card_id)) != 12:
                lcd.set_RGB(0, 0, 255)
                lcd.print_out("Kortet er")
                lcd.set_cursor(0, 1)
                lcd.print_out("Ugyldigt")
            # Hvis kortet allerede er i databasen.
            else:
                lcd.set_RGB(255, 0, 0)
                lcd.print_out("Kort allerede")
                lcd.set_cursor(0, 1)
                lcd.print_out("registeret")
            sleep(3)

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
