# esp32_lcd.py

from machine import Pin
import time

class LcdApi:
    """Implements the API for talking with HD44780 LCDs."""

    # The following constants are used to map characters to the LCD's
    # special character RAM.
    LCD_CHR_BAR_GRAPH_EMPTY = 0xa0
    LCD_CHR_BAR_GRAPH_1 = 0xa1
    LCD_CHR_BAR_GRAPH_2 = 0xa2
    LCD_CHR_BAR_GRAPH_3 = 0xa3
    LCD_CHR_BAR_GRAPH_4 = 0xa4
    LCD_CHR_BAR_GRAPH_5 = 0xa5
    LCD_CHR_BAR_GRAPH_6 = 0xa6
    LCD_CHR_BAR_GRAPH_7 = 0xa7
    LCD_CHR_BAR_GRAPH_FULL = 0xff

    def _init_(self, num_lines, num_columns):
        self.num_lines = num_lines
        if self.num_lines > 4:
            self.num_lines = 4
        self.num_columns = num_columns
        if self.num_columns > 40:
            self.num_columns = 40
        self.cursor_x = 0
        self.cursor_y = 0
        self.implied_newline = False
        self.backlight = True
        self.display_off()
        self.backlight_on()
        self.clear()
        self.hal_write_command(self.LCD_ENTRY_MODE_SET | self.LCD_ENTRY_LEFT)
        self.hide_cursor()
        self.display_on()

    def clear(self):
        """Clears the LCD display and moves the cursor to the top left."""
        self.hal_write_command(self.LCD_CLEAR_DISPLAY)
        self.hal_write_command(self.LCD_RETURN_HOME)
        self.cursor_x = 0
        self.cursor_y = 0

    def show_cursor(self):
        """Causes the cursor to be visible."""
        self.hal_write_command(self.LCD_DISPLAY_CONTROL | self.LCD_DISPLAY_ON | self.LCD_CURSOR_ON)

    def hide_cursor(self):
        """Causes the cursor to be hidden."""
        self.hal_write_command(self.LCD_DISPLAY_CONTROL | self.LCD_DISPLAY_ON)

    def blink_cursor_on(self):
        """Turns on the cursor, and makes it blink."""
        self.hal_write_command(self.LCD_DISPLAY_CONTROL | self.LCD_DISPLAY_ON | self.LCD_CURSOR_ON | self.LCD_CURSOR_BLINK_ON)

    def blink_cursor_off(self):
        """Turns on the cursor, but stops it from blinking."""
        self.hal_write_command(self.LCD_DISPLAY_CONTROL | self.LCD_DISPLAY_ON | self.LCD_CURSOR_ON)

    def display_on(self):
        """Turns on (i.e. unblanks) the LCD."""
        self.hal_write_command(self.LCD_DISPLAY_CONTROL | self.LCD_DISPLAY_ON)

    def display_off(self):
        """Turns off (i.e. blanks) the LCD."""
        self.hal_write_command(self.LCD_DISPLAY_CONTROL)

    def backlight_on(self):
        """Turns on the backlight."""
        self.backlight = True
        self.hal_set_backlight(True)

    def backlight_off(self):
        """Turns off the backlight."""
        self.backlight = False
        self.hal_set_backlight(False)

    def move_to(self, cursor_x, cursor_y):
        """Moves the cursor to the specified coordinates."""
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y
        addr = cursor_x & 0x3f
        if cursor_y & 1:
            addr += 0x40
        if cursor_y & 2:
            addr += self.num_columns
        self.hal_write_command(self.LCD_SET_DD_RAM_ADDR | addr)

    def putchar(self, char):
        """Writes the specified character to the LCD."""
        if char == '\n':
            if self.implied_newline:
                # self.implied_newline means we advanced to the next line
                # due to a previous character being written to the end of
                # the line. In this case, the received newline is ignored.
                pass
            else:
                self.cursor_x = self.num_columns
        else:
            self.hal_write_data(ord(char))
            self.cursor_x += 1
        if self.cursor_x >= self.num_columns:
            self.cursor_x = 0
            self.cursor_y += 1
            self.implied_newline = True
        else:
            self.implied_newline = False
        if self.cursor_y >= self.num_lines:
            self.cursor_y = 0
        self.move_to(self.cursor_x, self.cursor_y)

    def putstr(self, string):
        """Writes the specified string to the LCD."""
        for char in string:
            self.putchar(char)

    def custom_char(self, location, charmap):
        """Writes a custom character to the LCD."""
        location &= 0x7
        self.hal_write_command(self.LCD_SET_CG_RAM_ADDR | (location << 3))
        time.sleep_us(40)
        for i in range(8):
            self.hal_write_data(charmap[i])
        time.sleep_us(40)
        self.move_to(self.cursor_x, self.cursor_y)

    def hal_set_backlight(self, on):
        """
        Allows the hal to turn the backlight on and off.
        The default implementation does nothing.
        """
        pass

class GpioLcd(LcdApi):
    """
    Implements a HD44780 character LCD connected via GPIO pins.
    """
    # The following constants are commands needed by the HD44780 controller
    LCD_CLEAR_DISPLAY = 0x01
    LCD_RETURN_HOME = 0x02
    LCD_ENTRY_MODE_SET = 0x04
    LCD_DISPLAY_CONTROL = 0x08
    LCD_CURSOR_SHIFT = 0x10
    LCD_FUNCTION_SET = 0x20
    LCD_SET_CG_RAM_ADDR = 0x40
    LCD_SET_DD_RAM_ADDR = 0x80

    # The following constants are flags for the HD44780 controller
    LCD_ENTRY_RIGHT = 0x00
    LCD_ENTRY_LEFT = 0x02
    LCD_ENTRY_SHIFT_INCREMENT = 0x01
    LCD_ENTRY_SHIFT_DECREMENT = 0x00

    LCD_DISPLAY_ON = 0x04
    LCD_CURSOR_ON = 0x02
    LCD_CURSOR_BLINK_ON = 0x01

    LCD_DISPLAY_MOVE = 0x08
    LCD_CURSOR_MOVE = 0x00
    LCD_MOVE_RIGHT = 0x04
    LCD_MOVE_LEFT = 0x00

    LCD_8BIT_MODE = 0x10
    LCD_4BIT_MODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5X10_DOTS = 0x04
    LCD_5X8_DOTS = 0x00

def __init__(self, rs_pin, enable_pin, d4_pin, d5_pin, d6_pin, d7_pin,
             backlight_pin=None, num_lines=2, num_columns=16):
    # 1. Simpan pin-pin sebagai atribut DULU
    self.rs_pin = rs_pin
    self.enable_pin = enable_pin
    self.d4_pin = d4_pin
    self.d5_pin = d5_pin
    self.d6_pin = d6_pin
    self.d7_pin = d7_pin
    self.backlight_pin = backlight_pin

    # 2. Inisialisasi pin sebagai Output
    self.rs_pin.init(Pin.OUT)
    self.enable_pin.init(Pin.OUT)
    self.d4_pin.init(Pin.OUT)
    self.d5_pin.init(Pin.OUT)
    self.d6_pin.init(Pin.OUT)
    self.d7_pin.init(Pin.OUT)
    self.rs_pin.value(0)
    self.enable_pin.value(0)
    if self.backlight_pin:
        self.backlight_pin.init(Pin.OUT)

    # 3. Urutan perintah inisialisasi untuk mode 4-bit
    time.sleep_ms(20)   # Beri waktu LCD untuk menyala
    self.hal_write_command(0x33)
    self.hal_write_command(0x32)

    # 4. Atur fungsi LCD dan panggil __init__ dari parent class (LcdApi) di bagian PALING AKHIR
    self.hal_write_command(self.LCD_FUNCTION_SET | self.LCD_4BIT_MODE | self.LCD_2LINE | self.LCD_5X8_DOTS)
    super().__init__(num_lines, num_columns)

    def hal_write_command(self, cmd):
        """Writes a command to the LCD."""
        # Note: The hal_write_command function is called before LcdApi
        # is initialized.
        self.hal_write_nibble(cmd >> 4)
        self.hal_write_nibble(cmd)
        time.sleep_ms(5)

    def hal_write_data(self, data):
        """Write data to the LCD."""
        self.rs_pin.value(1)
        self.hal_write_nibble(data >> 4)
        self.hal_write_nibble(data)
        self.rs_pin.value(0)
        
    def hal_write_nibble(self, nibble):
        """Writes a 4-bit nibble to the LCD."""
        self.d4_pin.value(nibble & 0x01)
        self.d5_pin.value(nibble & 0x02)
        self.d6_pin.value(nibble & 0x04)
        self.d7_pin.value(nibble & 0x08)
        self.hal_pulse_enable()

    def hal_pulse_enable(self):
        """Pulse the enable line."""
        self.enable_pin.value(0)
        time.sleep_us(1)
        self.enable_pin.value(1)
        time.sleep_us(1)
        self.enable_pin.value(0)
        time.sleep_us(100)
    
    def hal_set_backlight(self, on):
        """Allows the hal to turn the backlight on and off."""
        if self.backlight_pin:
            self.backlight_pin.value(1 if on else 0)