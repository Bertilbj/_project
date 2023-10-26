import RPi.GPIO as G
from time import sleep
from typing import Callable

class LCD:
    class Cursor:
        
        def __init__(self, row: int = 0, col: int = 0, col_count: int = 16, line_addresses: list[int] = [0], write_function: Callable = None) -> None:
            self.row = row
            self.col = col
            self.row_count = len(line_addresses)
            self.col_count = col_count
            self.line_addresses = line_addresses
            self.write = write_function
        
        def increment(self) -> None:
            self.col += 1
            if self.col >= self.col_count:
                self.col = 0
                self.row += 1
                if self.row >= self.row_count:
                    self.row = 0
                self.set_cursor_pos(self.row, self.col)
        
        def set_cursor_pos(self, row: int, col: int) -> None:
            self.row = row
            self.col = col
            add = self.line_addresses[row] + col
            self.write(LCD.CMD_REG, 0x80 | (add & 0x7F))

    LINES_TWO = 0
    LINES_FOUR = 1
    FONT_5X8 = 0
    FONT_5X11 = 1

    CMD_REG = 0
    DATA_REG = 1

    def __init__(self, rs_pin: int, e_pin: int, d_pins: list[int], GPIO_mode=G.BCM, n_lines: int=LINES_TWO, font: int=FONT_5X8, n_cols=16, line_addresses: list[int] = [0]) -> None:

        G.setmode(GPIO_mode)
        G.setup(rs_pin, G.OUT)
        G.setup(e_pin, G.OUT, initial=G.LOW)
        G.setup(d_pins, G.OUT)

        self.rs_pin = rs_pin
        self.e_pin = e_pin
        self.data_pins = d_pins
        self.n_lines = n_lines
        self.mode = 8
        self.cursor = self.Cursor(col_count=n_cols, line_addresses=line_addresses, write_function=self.__write)
        
        if len(d_pins) == 8:  # Auto set mode from number of data pins provided
            self.mode = 8
            self.function_set(1, 0, 0)
            sleep(0.005)  # wait 5 ms
            self.function_set(1, 0, 0)
            sleep(0.0005)  # wait 500 us
            self.function_set(1, 0, 0)

            self.function_set(1, n_lines, font)
        else:
            self.__write(self.CMD_REG, 0x3)
            sleep(0.005)  # wait 5 ms
            self.__write(self.CMD_REG, 0x3)
            sleep(0.0005)  # wait 500 us
            self.__write(self.CMD_REG, 0x3)

            self.__write(self.CMD_REG, 0x2)

            self.mode = 4
            self.function_set(0, n_lines, font)

        self.display_on_off(0, 1, 1)
        self.clear_display()
        self.entry_mode_set(1, 0)
        self.display_on_off(1, 1, 1)
    
    def __write(self, reg: int, data: int) -> None:
        G.output(self.rs_pin, reg)

        if self.mode == 4:     # Only clock if
            msn = data >> 4  # Most Significant Nibble
            lsn = data & 0x0F  # Least Significant Nibble

            for i in self.data_pins:
                G.output(i, msn & 1)
                msn = msn >> 1

            G.output(self.e_pin, G.HIGH)
            sleep(0.000001)  # wait 1 us
            G.output(self.e_pin, G.LOW)

            for i in self.data_pins:
                G.output(i, lsn & 1)
                lsn = lsn >> 1
        else:
            for i in self.data_pins:
                G.output(i, data & 1)
                data = data >> 1

        G.output(self.e_pin, G.HIGH)
        sleep(0.000001)  # wait 1 us
        G.output(self.e_pin, G.LOW)

    def write_char(self, c: str) -> None:
        self.__write(self.DATA_REG, ord(c))
        self.cursor.increment()

    def write_string(self, s: str) -> None:
        for c in s:
            self.write_char(c)

    def clear_display(self) -> None:
        self.__write(self.CMD_REG, 0x01)
        sleep(0.002)

    def return_home(self) -> None:
        self.__write(self.CMD_REG, 0x02)
        sleep(0.002)

    def entry_mode_set(self, i_d: int, sh: int) -> None:
        self.__write(self.CMD_REG, 0x04 | (i_d & 1) << 1 | (sh & 1))
        sleep(0.00004)

    def display_on_off(self, d: int, c: int, b: int) -> None:
        self.__write(self.CMD_REG,0x08 | (d & 1) << 2 | (c & 1) << 1 | (b & 1))
        sleep(0.00004)

    def cursor_display_shift(self, sc: int, rl: int) -> None:
        self.__write(self.CMD_REG, 0x10 | (sc & 1) << 3 | (rl & 1) << 2)
        sleep(0.00004)

    def function_set(self, dl: int, n: int, f: int) -> None:
        self.__write(self.CMD_REG, 0x20 | (dl & 1) << 4 | (n & 1) << 3 | (f & 1) << 2)
        sleep(0.00004)

    def set_cgram_address(self, add: int) -> None:
        self.__write(self.CMD_REG, 0x40 | (add & 0x3F))

    def create_custom_char(self, add: int, char: list[int]) -> None:
        self.set_cgram_address(add)
        for row in char:
            self.__write(self.DATA_REG, row)

if __name__ == "__main__":
    G.setwarnings(False)
    data_pins = [27, 22, 23, 24, 25, 5, 6, 26]
    #data_pins = [25, 5, 6, 26]
    screen = LCD(rs_pin=17, e_pin=4, d_pins=data_pins, GPIO_mode=G.BCM, n_lines=LCD.LINES_FOUR, font=LCD.FONT_5X8, n_cols=16, line_addresses=[0x00, 0x40, 0x14, 0x54])
   
    # screen.create_custom_char(0, cc.wink)
    # screen.create_custom_char(8, cc.smiley)
    # screen.create_custom_char(16, cc.padlock)
    # screen.create_custom_char(24, cc.key)
    # screen.create_custom_char(32, cc.bell)

    # screen.return_home()

    #screen.write_string('ABCDEFGHIJKL')
    #screen.cursor.set_cursor_pos(1,14)
    screen.write_string('ABCDEFGHIJKL')
    screen.write_char('A')
    print("Running internal test")
    #for i in range(10):
    #    screen.write_string("ABCDEFGHIJKLMNOP")
    #    sleep(2)
    screen.clear_display()

    

    # screen.write_char(chr(0))
    # screen.write_char(chr(1))
    # screen.write_char(chr(2))
    # screen.write_char(chr(3))
    # screen.write_char(chr(4))
