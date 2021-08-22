# SLT-Data-Usage
This program can get your SLT data usage and display it in the system tray.
||||
:-------------------------:|:-------------------------:|:-------------------------:
![Summary](https://user-images.githubusercontent.com/12431727/128629535-049ef77a-0754-4616-993e-41b22bf6ff69.png) | ![SLT Usage Report on Windows](https://user-images.githubusercontent.com/12431727/128629534-794db86c-1296-46d4-b0c9-106e5fe4d152.png) | ![SLT Usage Report on MacOS](https://user-images.githubusercontent.com/12431727/129947902-0a71adde-b447-4ef4-a202-f80806ee827c.png)|
_Summary is always visible_ | _Hover over to see the full report_ | _Same on MacOS_ |

Tested on Windows (10) and MacOS (Big Sur).
_For OSX Xbar plugin, see [@kaveenr](https://gist.github.com/kaveenr/a820616adf2f5d9d82db1b1250bf15f3#file-readme-md)'s script._

--------------------------------------


### Download and install the [latest](https://github.com/kmchmk/SLT-Data-Usage/releases/latest) version using following instructions.

#### How to install to run forever:

Prerequisites:
* Windows 10, Mac computer
* [SLT broadband](https://internetvas.slt.lk/login) account credentials

How to install:

## Windows

1. Download the [SLT_Usage_Web_Installer.exe](https://github.com/kmchmk/SLT-Data-Usage/releases/download/v1.3/SLT_Usage_Web_Installer.exe) file. Your browser may hesitate, so you may have to allow it in the Downloads section.
2. Install the downloaded file.
2. App will start automatically after the installation.
3. Save your SLT username (Ex: 94112xxxxxx) and password using the popup window.
4. You will see a system tray icon with your data usage summary. Left click on it to refresh and hover over to see the full report.
5. Move it out to the taskbar from system tray, if you want to see it directly all the time.

## MacOS

1. Download the  [SLT_Usage.zip](https://github.com/kmchmk/SLT-Data-Usage/releases/latest/download/SLT_Usage.zip) file.
2. Drag the downloaded file to Applications folder.
3. Go to Applications folder, right click on the app icon and select open. You might not be able to run the app using launchpad at first.
4. Save your SLT username (Ex: 94112xxxxxx) and password using the popup window.
5. You will see a system tray icon with your data usage summary. Hover over to see the full report.
6. Set the app to start at login. See here: [Mac OS X: Change Which Apps Start Automatically at Login](https://www.howtogeek.com/206178/mac-os-x-change-which-apps-start-automatically-at-login/)

_Auto refresh interval is 120 secs._

--------------------------------------

### 🟥 Following instructions are for developers only.

##### If you are running/building from code

Initial setup:
```
# For all OSs
pip install pystray requests darkdetect

# For Ubuntu
sudo apt install gir1.2-appindicator3-0.1
sudo apt install python3-tk
sudo apt purge fcitx-module-dbus

# For MacOS
brew install python-tk
```

To run from code:
```
python3 SLT_Usage.py
```

Create executable:
```
# For all OSs
pip3 install pyinstaller

# For Windows
pyinstaller --hidden-import 'pystray._win32' --noconsole --onefile 'SLT_Usage.py'

# For Ubuntu
pyinstaller --hidden-import 'pystray._appindicator' --hidden-import 'pystray._gtk' --hidden-import 'pystray._xorg' --noconsole --onefile 'SLT_Usage.py'

# For MacOS
pyinstaller --hidden-import 'pystray._darwin' --noconsole --onefile 'SLT_Usage.py'
```

Create [InnoSetup](https://jrsoftware.org/isinfo.php) installer:
```
iscc InnoSetup_offline_installer_script.iss
iscc InnoSetup_web_installer_script.iss
```
