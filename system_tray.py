from warnings import filterwarnings
import pystray
from PIL import Image, ImageDraw, ImageFont
import time
import random
import threading
import sys
import data_usage
import input_ui

size = 100
font_type = ImageFont.truetype("arial.ttf", size//2)
TOP_LEFT = (0, 0)
def get_empty_image(): return Image.new('RGBA', (size, size//2))  # Empty image


finished = False
refresh_itr_duration = 120  # seconds
stop_itr_duration = 3  # seconds


def refresh(icon):
    image = get_empty_image()
    draw = ImageDraw.Draw(image)
    # ToDo - I used yellow below because of the System wide Dark theme
    draw.text(TOP_LEFT, data_usage.get_data_usage(),
              font=font_type, fill='yellow')
    icon.icon = image


# Exit method should be faster than refresh interval. So we have 2 iterations here.
def update_forever(icon):
    refresh(icon)
    seconds_passed = 0
    while not finished:
        time.sleep(stop_itr_duration)
        seconds_passed += stop_itr_duration
        if seconds_passed >= refresh_itr_duration:
            refresh(icon)
            seconds_passed = 0


def exit_method(icon):
    global finished
    finished = True
    icon.stop()


menu = (pystray.MenuItem('Refresh', refresh), pystray.MenuItem(
    'Change account', input_ui.change_account), pystray.MenuItem('Exit', exit_method))
icon = pystray.Icon("icon1", get_empty_image(), "SLT Daily Usage (GB)", menu)
icon.visible = True
icon.run(setup=update_forever)
icon.stop()
