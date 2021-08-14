# SLT-Data-Usage
This program can get your SLT data usage and display it in the system tray.
|||
:-------------------------:|:-------------------------:
![Summary](https://user-images.githubusercontent.com/12431727/128629535-049ef77a-0754-4616-993e-41b22bf6ff69.png) |  ![SLT Usage Report](https://user-images.githubusercontent.com/12431727/128629534-794db86c-1296-46d4-b0c9-106e5fe4d152.png)
_Summary is always visible_        |  _Hover over to see the full report_

Tested only on Windows 10.
_For OSX see [@kaveenr](https://gist.github.com/kaveenr/a820616adf2f5d9d82db1b1250bf15f3#file-readme-md)'s script._

--------------------------------------


### Download and install the [latest](https://github.com/kmchmk/SLT-Data-Usage/releases/latest) version using following instructions.

#### How to install to run forever:

Prerequisites:
* Windows 10 machine
* SLT broadband [account](https://internetvas.slt.lk/login) credentials

Steps:

1. Download the [SLT_Usage_Web_Installer.exe](https://github.com/kmchmk/SLT-Data-Usage/releases/download/v1.3/SLT_Usage_Web_Installer.exe) file. Your browser may hesitate, so you may have to allow it in the Downloads section.
2. Install the downloaded file.
2. App will start automatically after the installation.
3. Save your SLT username (Ex: 94112xxxxxx) and password using the popup window.
4. You will see a system tray icon containing "X" mark. Right click it and "Refresh".
5. Move it out to the taskbar from system tray, if you want to see it directly all the time.

_Auto refresh interval is 120 secs._

--------------------------------------

### Following instructions are for developers only.

##### If you are running/building from code

Initial setup:
```
# For all OSs
pip install pystray requests

# For Ubuntu
sudo apt install gir1.2-appindicator3-0.1
sudo apt install python3-tk
sudo apt purge fcitx-module-dbus
```

To run from code:
```
python SLT_Usage.py
```

Create executable:
```
pip install pyinstaller
pyinstaller --hidden-import 'pystray._win32' --noconsole --onefile 'SLT_Usage.py'
```

Create [InnoSetup](https://jrsoftware.org/isinfo.php) installer:
```
iscc InnoSetup_offline_installer_script.iss
iscc InnoSetup_web_installer_script.iss
```
