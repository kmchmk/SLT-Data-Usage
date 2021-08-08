# SLT-Data-Usage
This program can get your SLT data usage and display it in the system tray.
Tested only on Windows 10.

For OSX : [@kaveenr](https://gist.github.com/kaveenr/a820616adf2f5d9d82db1b1250bf15f3#file-readme-md)

--------------------------------------

#### Summary is always visible.

![image](https://user-images.githubusercontent.com/12431727/128552259-83c8b8ea-4b40-476a-ad6d-f8761d81604a.png)

--------------------------------------

#### Hover over to see the full report.

![SLT Usage Report](https://user-images.githubusercontent.com/12431727/128612361-5a16e5c8-4857-4e9f-8283-acf9ce5e96b3.png)

--------------------------------------

Download and run the [latest executable](https://github.com/kmchmk/SLT-Data-Usage/releases/latest).

Refresh interval is 120 secs, but it can easily be changed in the code.

--------------------------------------

### Following instructions are for developers only.

##### If you are building from code

Initial setup:
```
pip install pystray
pip install requests
```

Create executable:
```
pyinstaller --noconsole --onefile 'system_tray.py' --name 'SLT_Usage'
```
