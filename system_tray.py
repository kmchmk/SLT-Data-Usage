import pystray._win32
from PIL import Image, ImageDraw, ImageFont
import time
import data_usage
import input_ui

size = 100
font_type = ImageFont.truetype("tahoma.ttf", size//2)
TOP_LEFT = (0, 0)
current_data_usage = data_usage.DataUsage()
refresh_itr_duration = 120  # seconds


def get_empty_image(): return Image.new('RGBA', (size, size//2))  # Empty image


def refresh(icon):
    image = get_empty_image()
    draw = ImageDraw.Draw(image)
    # ToDo - I used yellow below because of the System wide Dark theme
    current_data_usage.refresh()
    draw.text(TOP_LEFT, current_data_usage.get_summary(),
              font=font_type, fill='yellow')
    icon.icon = image
    icon.title = current_data_usage.get_usage_report()


def update_forever(icon):
    icon.visible = True
    while icon.visible:
        refresh(icon)
        time.sleep(refresh_itr_duration)
    icon.stop()


def exit_method(icon):
    icon.visible = False


menu = (pystray.MenuItem('Refresh', refresh),
        pystray.MenuItem('Change account', input_ui.change_account),
        pystray.MenuItem('Exit', exit_method))
icon = pystray.Icon("icon_name", get_empty_image(), "Starting...", menu)

icon.run(update_forever)
