# paper-io-game-bot
A simple python game bot for the classic mode paper.io game.
The game bot takes control of your mouse to play the game.

## Very detailed quick start guide:
1. Start the script in a Terminal window before playing. (Use normal user privilege, not root privilege)
$ python3 ./paper-io.py
1. Go to your browser (for instance Firefox, Google Chrome), press F11 to full screen your experience, and start game.
1. If the game doesn't start right away because of an ad playing, the script won't take control of your mouse until the game starts. You can either wait until the ad finishes, or click skip on the ad to skip it. Clicking on other things can make the script fail.
1. Before the game starts, you can stop the script by going back to the Terminal window, and press the keys Control and c at the same time (Ctrl+c). This "kills" the script. The game bot will not run until you start it again, and the following step won't apply any more.
1. After the game starts, the script controls your mouse and moves it near the middle of your screen. You can still try and move your mouse, but the script will interrupt you from time to time.
1. There are two ways to stop the script after you start playing. One is to go back to the Terminal window and press Ctrl+c. The other is to keep moving you mouse into any one of the 4 corners of your screen, as much as possible, against the script, for a few seconds.
1. If you care, debug logs are created under the "history" folder.

## Platform
The performance of the script (i.e. how well it scores in the game) depends heavily on proper tuning on the specific machine.
This set of scripts are only tuned on a particular Ubuntu 20.04 (4GB RAM, 4 CPU) virtual machine hosted by Hyper-V.

### Python dependencies
Python 3.8.10

The following python packages need to be installed before the script can run.
$ pip3 install Pillow
$ pip3 install pyautogui
$ pip3 install cv2

### Tuning considerations
The scripts were tuned by repeatedly running the game bot to see how well it plays, and then changing "magic numbers" (search "magic numbers in programming" if you are confused). Sometimes it was also necessary to completely change how the game bot plays.
The scripts blindly follows timed instructions like "move right for 1 second then move down for 0.5 seconds" and so on.
Choice of browser, CPU speed, CPU throttling when power is unplugged can all be potential factors that improve or decrease game bot performance.
For ease of use, make terminal emulator window "Always On Top", and leave it in one of the corners of your screen.
