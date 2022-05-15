# twd_bhaptics
A bhaptics integration mod into The Walking Dead Saints & Sinners
```diff
- This mod only supports ONLY the following game version: 2021.12.08 / build 218977-STAGE
```
## Features:
Demonstration video on YouTube:<br />
[![](https://img.youtube.com/vi/ScSQjtlFqtc/0.jpg)](http://www.youtube.com/watch?v=ScSQjtlFqtc)

* Gunshot haptics (one-handed or two handed) on arms and vest
* Zombie attacks haptics dependent on the direction
* Get shots
* Low health heart beat
* Low endurance lung contraction
* Grabbing and placing backpack haptics
* Grabbing and placing items on the right shoulder haptics
* Eating-haptics
* Healing haptics

Currently uses Tactosy for Arms and the Tactsuit (X40/X16) 

## How To Use (easy)

* Clone or download the repository. Then just start ```twd_bhaptics.exe``` while the game is open or before you are opening the game.
* Once you closed the game you have to restart the mod!

## How To Use (using a Python interpreter)
 Don't want to run a prebuild .exe? This is python project so just run the ```starter.py``` with a Python3.9 interpreter.
 You need to install the following dependencys:
 
*  ```pip install websocket websocket-client```

## Known issues
This mod is more like what is often called a "Trainer", so it reads certain memory addresses of the game. This leads to the following issues:

* If the player holds two guns in each of the hands, fast shots behind one another of the gun grabbed first are not recognised.
* Skript can't detect if the game was closed, you have to abort the script manually using STRG+C (or just close the window) 
* Unintended haptics while loading a level: values of the memory addresses are going crazy while loading a level

## Will this mod be updated for upcoming updates of the game?
Probably not. It is very likely that the smallest update shifts the memory offsets, which means that the whole mod is not working anymore.
Finding these offsets was the main workload creating this mod. Since it is OpenSource you are welcomed to search for broken offsets by yourself and therefore
help me to fix it!

Since then you have to [download the exact supported version](https://steamcommunity.com/sharedfiles/filedetails/?id=889624474).
By time the writing this, the supported version is the newest steam version.

## Credits & Libs
Thanks to [Florian Fahrenberger](https://github.com/floh-bhaptics) for his heavy testing and the haptic-patterns!

* [PyMeow](https://github.com/qb-0/PyMeow)
* [tact-python](https://github.com/bhaptics/tact-python)
* [pyinstaller](https://github.com/pyinstaller/pyinstaller)

If you have any suggestions, feel free to open an Issue.
