# SLT-Data-Usage
This program can get your SLT data usage and display it in the system tray.

![image](https://user-images.githubusercontent.com/12431727/128552259-83c8b8ea-4b40-476a-ad6d-f8761d81604a.png)

Download and run the [latest executable](https://github.com/kmchmk/SLT-Data-Usage/releases/latest).

Refresh interval is 120 secs, but it can easily be changed in the code.


### If you are building from code

Initial setup:
```
pip install pystray
pip install requests
```

Create executable:
```
pyinstaller --noconsole --onefile 'system_tray.py' --name 'SLT_Usage'
```
