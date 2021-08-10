# SLT-Data-Usage
This program can get your SLT data usage and display it in the system tray.
|||
:-------------------------:|:-------------------------:
![Summary](https://user-images.githubusercontent.com/12431727/128629535-049ef77a-0754-4616-993e-41b22bf6ff69.png) |  ![SLT Usage Report](https://user-images.githubusercontent.com/12431727/128629534-794db86c-1296-46d4-b0c9-106e5fe4d152.png)
_Summary is always visible_        |  _Hover over to see the full report_

Tested only on Windows 10.
_For OSX see [@kaveenr](https://gist.github.com/kaveenr/a820616adf2f5d9d82db1b1250bf15f3#file-readme-md)'s script._

--------------------------------------


### Download and install the [latest executable](https://github.com/kmchmk/SLT-Data-Usage/releases/latest) using following instructions.

#### How to install to run forever:

Prerequisites:
* Windows 10 machine
* SLT broadband [account](https://internetvas.slt.lk/login) credentials

Steps:

1. Go to the [latest release](https://github.com/kmchmk/SLT-Data-Usage/releases/latest) page and expand "Assets" section.
2. Download the SLT_Usage_\<version\>.zip. Your browser may hesitate, so you may have to allow it in the Downloads section.
3. Extract the downloaded zip and you will find the SLT_Usage.exe file inside it.
4. Copy the SLT_Usage.exe file to any location. Do not paste if it asks for admin permissions to continue.
   (Recommended location: C:\\Users\\%USERPROFILE%\\AppData\\Local\\Programs\\SLT_Usage\\SLT_Usage.exe)
5. Right click on the SLT_Usage.exe in new location and select "Copy".
6. Go to C:\\Users\\%USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\
7. Right click on the background and select "Paste shortcut".
8. Double click the new shortcut and save your SLT username (Ex: 94112xxxxxx) and password using the popup window.
9. You will see a system tray icon containing "X" mark. Right click it and "Refresh".
10. Move it out to the taskbar from system tray, if you want to see it directly all the time.

_Auto refresh interval is 120 secs._

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
Create [InnoSetup](https://jrsoftware.org/isinfo.php) installer:
```
iscc InnoSetup_offline_installer_script.iss
iscc InnoSetup_web_installer_script.iss
```
