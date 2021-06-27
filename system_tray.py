from warnings import filterwarnings
import pystray
from PIL import Image, ImageDraw, ImageFont
import time, random, threading, sys
import data_usage

size = 100
font_type  = ImageFont.truetype("arial.ttf", size//2)
TOP_LEFT = (0,0)
def get_empty_image(): return Image.new('RGBA', (size, size//2)) # Empty image
finished = False
refresh_itr_duration = 120 #seconds
stop_itr_duration = 3 #seconds
def refresh(icon):
    image = get_empty_image()
    draw = ImageDraw.Draw(image)
    draw.text(TOP_LEFT, data_usage.get_data_usage(), font = font_type, fill = 'yellow') # ToDo - I used yellow here because of the System wide Dark theme
    icon.icon = image

def update_forever(icon): # Exit method should be faster than refresh interval. So we have 2 iterations here.
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

menu = (pystray.MenuItem('Refresh', refresh), pystray.MenuItem('Exit', exit_method))
icon = pystray.Icon("icon1", get_empty_image(), "SLT Daily Usage (GB)", menu)
icon.visible = True
icon.run(setup=update_forever)
icon.stop()