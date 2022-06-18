# https://github.com/learncodebygaming/enb_bot/blob/master/timing_bot/main.py
import math, sys, numpy, logging, os
import pyautogui
import time
from PIL import Image, ImageStat

# set up folder for game session
GAME_SESSION_FOLDER = os.path.join(os.getcwd(), "history", time.strftime('%Y-%m-%d %H:%M %Z', time.localtime(time.time())))
os.mkdir(GAME_SESSION_FOLDER)
# set up logging for debugging purposes
logging.basicConfig(filename=os.path.join(GAME_SESSION_FOLDER, 'paper-io.log'), level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.getLogger('PIL').setLevel(logging.WARNING)

# This script automates the playing of paper.io game
# for the case where we spawn away from any edge.
# In other cases this script quickly loses the game.
# This script was tuned on 4G 4CPU Hyper-V Ubuntu 20,
# with Helios 300 power unplugged.

# Run this script before clicking Play.

# this is the number of seconds we draw an edge of a square
SQUARE_SIZE = 0.6
# screen size
(SCREEN_WIDTH, SCREEN_HEIGHT) = pyautogui.size()
# the images that tell us our game has begun or ended
GAME_START_IMAGE = Image.open("./skeleton_head.png")
GAME_END_IMAGE = Image.open("./twitter.png")
# the coordinates to find those images
GAME_TELLER_REGION = (0, 0, round(SCREEN_WIDTH / 8), round(SCREEN_HEIGHT / 4))
GAME_END_CHECK_FREQENCY = 3

def main():
    initializePyAutoGUI()

    print("Please full-screen your browser (press F11), start the game,")
    print("and leave your mouse in the center of screen.\n")

    # wait for the game to start
    foundImage = None
    print("Waiting for the game to start...", end = '', flush = True)

    while not isGameStarted():
        # wait for the game to start...
        print(".", end = '', flush = True)

    print("\nGame has started!")

    # If we trace a path that meets back with itself then we lose,
    # so open paths are dangerous.
    # When we first start, we begin with such an open path.
    # We can be safer if we build a base/foothold, free of such open paths.
    buildBase()

    # now that we have a safe foothold, we can deploying any strategy
    # we like to beat the game!
    print("A safe base has been built. Good luck with your game!")

    buildSquares(SQUARE_SIZE)
    # start spiral expansion
    #                  <---^
    #                  |<-^|
    #                  ||*||
    #                  |v->|
    #                  v--->
    # spiral = 1
    spiral_order = ['right', 'up', 'left', 'down']
    level = 1
    while True:
        movePlayer('down', SQUARE_SIZE)
        spiralEdge(level, 'right', SQUARE_SIZE)
        movePlayer('up', SQUARE_SIZE)
        spiralEdge(level, 'up', SQUARE_SIZE)
        movePlayer('left', SQUARE_SIZE)
        spiralEdge(level, 'left', SQUARE_SIZE)
        movePlayer('down', SQUARE_SIZE)
        spiralEdge(level, 'down', SQUARE_SIZE)
        level = level + 1


def initializePyAutoGUI():
    # Initialized PyAutoGUI
    # https://pyautogui.readthedocs.io/en/latest/introduction.html
    # When fail-safe mode is True, moving the mouse to the upper-left corner will abort your program.
    pyautogui.FAILSAFE = True

def isGameStarted():
    foundImage = pyautogui.locateOnScreen(GAME_START_IMAGE, grayscale=True, region=GAME_TELLER_REGION, confidence=0.8)
    return foundImage != None

def isGameFinished():
    foundImage = pyautogui.locateOnScreen(GAME_END_IMAGE, grayscale=True, region=GAME_TELLER_REGION, confidence=0.8)
    return foundImage != None

def saveScore():
    time.sleep(1) # wait a bit for scores to show
    SCORE_BOX = (round(SCREEN_WIDTH * (5 / 12)), 0, round(SCREEN_WIDTH / 6), round(SCREEN_HEIGHT / 4))
    screenshot = pyautogui.screenshot(region=SCORE_BOX)
    screenshot.save(os.path.join(GAME_SESSION_FOLDER, "score.png"));

moveCount = 0
def movePlayer(key, seconds=1.00):
    global moveCount
    moveCount = moveCount + 1
    if key == 'up':
        pyautogui.moveTo(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)
    elif key == 'down':
        pyautogui.moveTo(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)
    elif key == 'left':
        pyautogui.moveTo(SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 2)
    elif key == 'right':
        pyautogui.moveTo(SCREEN_WIDTH / 2 + 50, SCREEN_HEIGHT / 2)
    else:
        pass

    time.sleep(seconds)
    if moveCount % GAME_END_CHECK_FREQENCY == 0:
        if isGameFinished():
            saveScore()
            sys.exit('The game seems to be finished.')

# https://stackoverflow.com/questions/3490727
def calculatePerceivedBrightness(img):
    stat = ImageStat.Stat(img)
    r,g,b = stat.mean
    return math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))

# get the moving direction in terms of one of the 4 quadrants,
#         \ u(p)  /
#      2l  \2u|1u/  1r
#           \ | /
# l(eft)------|------ r(ight)
#           / | \
#          /  |  \
#      3l / 3d|4d \ 4r
#           d(own)
# combined with 'up', 'down', 'left' and 'right'.
def getPlayerDirection(delay = 0):
    startTime = time.time() # keep track of how long we are taking...

    # a box that completely contains the player (top_left_x_y, width, height)
    # 300x300 pixels
    PLAYER_BOX = (SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2 - 150, 300, 300)
    # we look at a smaller box (100x100 pixels) inside the first box
    SMALLER_PLAYER_BOX_TOP_EDGE = (100, 100, 200, 101)
    SMALLER_PLAYER_BOX_TOP_EDGE_LEFT_HALF = (100, 100, 150, 101)
    SMALLER_PLAYER_BOX_TOP_EDGE_RIGHT_HALF = (150, 100, 200, 101)
    SMALLER_PLAYER_BOX_BOTTOM_EDGE = (100, 199, 200, 200)
    SMALLER_PLAYER_BOX_BOTTOM_EDGE_LEFT_HALF = (100, 199, 150, 200)
    SMALLER_PLAYER_BOX_BOTTOM_EDGE_RIGHT_HALF = (150, 199, 200, 200)
    SMALLER_PLAYER_BOX_LEFT_EDGE = (100, 100, 101, 200)
    SMALLER_PLAYER_BOX_LEFT_EDGE_TOP_HALF = (100, 100, 101, 150)
    SMALLER_PLAYER_BOX_LEFT_EDGE_BOTTOM_HALF = (100, 150, 101, 200)
    SMALLER_PLAYER_BOX_RIGHT_EDGE = (199, 100, 200, 200)
    SMALLER_PLAYER_BOX_RIGHT_EDGE_TOP_HALF = (199, 100, 200, 150)
    SMALLER_PLAYER_BOX_RIGHT_EDGE_BOTTOM_HALF = (199, 150, 200, 200)
    # brightness along the 4 edges of the smaller box
    top = 0
    topEdgeLeftHalf = 0
    topEdgeRightHalf = 0
    bottom = 0
    bottomEdgeLeftHalf = 0
    bottomEdgeRightHalf = 0
    left = 0
    leftEdgeTopHalf = 0
    leftEdgeBottomHalf = 0
    right = 0
    rightEdgeTopHalf = 0
    rightEdgeBottomHalf = 0

    # the game takes a little time to show everything
    # so wait this many seconds before checking player direction
    WAIT_TO_SEE_PLAYER = 0.1
    time.sleep(WAIT_TO_SEE_PLAYER)
    logging.debug("Waiting %.2f seconds to check moving direction..." %(WAIT_TO_SEE_PLAYER))
    screenshot = pyautogui.screenshot(region=PLAYER_BOX)
    screenshot.save(os.path.join(GAME_SESSION_FOLDER, "start_out_direction.png"));

    top = calculatePerceivedBrightness(screenshot.crop(SMALLER_PLAYER_BOX_TOP_EDGE))
    topEdgeLeftHalf = calculatePerceivedBrightness(screenshot.crop(SMALLER_PLAYER_BOX_TOP_EDGE_LEFT_HALF))
    topEdgeRightHalf = calculatePerceivedBrightness(screenshot.crop(SMALLER_PLAYER_BOX_TOP_EDGE_RIGHT_HALF))

    bottom = calculatePerceivedBrightness(screenshot.crop(SMALLER_PLAYER_BOX_BOTTOM_EDGE))
    bottomEdgeLeftHalf = calculatePerceivedBrightness(screenshot.crop(SMALLER_PLAYER_BOX_BOTTOM_EDGE_LEFT_HALF))
    bottomEdgeRightHalf = calculatePerceivedBrightness(screenshot.crop(SMALLER_PLAYER_BOX_BOTTOM_EDGE_RIGHT_HALF))

    left = calculatePerceivedBrightness(screenshot.crop(SMALLER_PLAYER_BOX_LEFT_EDGE))
    leftEdgeTopHalf = calculatePerceivedBrightness(screenshot.crop(SMALLER_PLAYER_BOX_LEFT_EDGE_TOP_HALF))
    leftEdgeBottomHalf = calculatePerceivedBrightness(screenshot.crop(SMALLER_PLAYER_BOX_LEFT_EDGE_BOTTOM_HALF))

    right = calculatePerceivedBrightness(screenshot.crop(SMALLER_PLAYER_BOX_RIGHT_EDGE))
    rightEdgeTopHalf = calculatePerceivedBrightness(screenshot.crop(SMALLER_PLAYER_BOX_RIGHT_EDGE_TOP_HALF))
    rightEdgeBottomHalf = calculatePerceivedBrightness(screenshot.crop(SMALLER_PLAYER_BOX_RIGHT_EDGE_BOTTOM_HALF))

    SMALL_DIFFERENCE = 5
    # if all 4 edges of the box are more or less the same,
    # then the screen really hasn't showed anything
    if abs(top-bottom) < SMALL_DIFFERENCE and abs(top-left) < SMALL_DIFFERENCE and abs(top-left) < SMALL_DIFFERENCE and abs(top-right) < SMALL_DIFFERENCE:
        return getPlayerDirection(delay + time.time() - startTime)

    # whichever direction the player moves, the opposite
    # direction will have the darkest colour
    listOfBrght = [topEdgeLeftHalf, topEdgeRightHalf, bottomEdgeLeftHalf, bottomEdgeRightHalf, leftEdgeTopHalf, leftEdgeBottomHalf, rightEdgeTopHalf, rightEdgeBottomHalf]
    listSorted = numpy.argsort(listOfBrght) # sorted indices
                                            # sorted from small to big
    logging.debug("Brightness: topEdgeLeftHalf %.2f, topEdgeRightHalf %.2f, bottomEdgeLeftHalf %.2f, bottomEdgeRightHalf %.2f, leftEdgeTopHalf %.2f, leftEdgeBottomHalf %.2f, rightEdgeTopHalf %.2f, rightEdgeBottomHalf %.2f." %(topEdgeLeftHalf, topEdgeRightHalf, bottomEdgeLeftHalf, bottomEdgeRightHalf, leftEdgeTopHalf, leftEdgeBottomHalf, rightEdgeTopHalf, rightEdgeBottomHalf))
    edge1 = listSorted[0] # the darkest
    edge2 = listSorted[1] # second darkest
    darkest = [edge1, edge2]
    darkest.sort()
    logging.debug("The darkest two edges: %d, %d." %(edge1, edge2))

    totalTime = delay + time.time() - startTime

    VERY_BRIGHT_BRIGHTNESS = 220

    a = 0
    b = 1
    if [a,b] == darkest:
        if abs(listOfBrght[a] - listOfBrght[b]) < SMALL_DIFFERENCE:
            return ("d", totalTime)
        if listOfBrght[a] > listOfBrght[b]:
            return ("3d", totalTime)
        else:
            return ("4d", totalTime)

    a = 2
    b = 3
    if [a,b] == darkest:
        if abs(listOfBrght[a] - listOfBrght[b]) < SMALL_DIFFERENCE:
            return ("u", totalTime)
        if listOfBrght[a] > listOfBrght[b]:
            return ("2u", totalTime)
        else:
            return ("1u", totalTime)

    a = 4
    b = 5
    if [a,b] == darkest:
        if abs(listOfBrght[a] - listOfBrght[b]) < SMALL_DIFFERENCE:
            return ("r", totalTime)
        if listOfBrght[a] > listOfBrght[b]:
            return ("1r", totalTime)
        else:
            return ("4r", totalTime)
    
    a = 6
    b = 7
    if [a,b] == darkest:
        if abs(listOfBrght[a] - listOfBrght[b]) < SMALL_DIFFERENCE:
            return ("l", totalTime)
        if listOfBrght[a] > listOfBrght[b]:
            return ("2l", totalTime)
        else:
            return ("3l", totalTime)
    
    a = 0
    b = 4
    if [a,b] == darkest:
        if listOfBrght[a] > listOfBrght[b]:
            return ("4r", totalTime)
        else:
            return ("4d", totalTime)
    
    a = 2
    b = 5
    if [a,b] == darkest:
        if listOfBrght[a] > listOfBrght[b]:
            return ("1r", totalTime)
        else:
            return ("1u", totalTime)
    
    a = 1
    b = 6
    if [a,b] == darkest:
        if listOfBrght[a] > listOfBrght[b]:
            return ("3l", totalTime)
        else:
            return ("3d", totalTime)
    
    a = 3
    b = 7
    if [a,b] == darkest:
        if listOfBrght[a] > listOfBrght[b]:
            return ("2l", totalTime)
        else:
            return ("2u", totalTime)

    # if not in any of the above cases, then start over again
    return getPlayerDirection(delay + totalTime)
    
def buildBase():
    # in which direction are we moving?
    (playerDirection, delay) = getPlayerDirection()
    if playerDirection[0] == '1':
        description = "we are moving into the 1st quadrant, "
        if playerDirection[1] == 'u':
            description = description + "heading up"
        if playerDirection[1] == 'r':
            description = description + "heading right"
    elif playerDirection[0] == '2':
        description = "we are moving into the 2nd quadrant, "
        if playerDirection[1] == 'u':
            description = description + "heading up"
        if playerDirection[1] == 'l':
            description = description + "heading left"
    elif playerDirection[0] == '3':
        description = "we are moving into the 3rd quadrant, "
        if playerDirection[1] == 'l':
            description = description + "heading left"
        if playerDirection[1] == 'd':
            description = description + "heading down"
    elif playerDirection[0] == '4':
        description = "we are moving into the 4th quadrant, "
        if playerDirection[1] == 'r':
            description = description + "heading right"
        if playerDirection[1] == 'd':
            description = description + "heading down"
    elif playerDirection[0] == 'u':
        description = "we are heading up"
    elif playerDirection[0] == 'd':
        description = "we are heading down"
    elif playerDirection[0] == 'l':
        description = "we are heading left"
    elif playerDirection[0] == 'r':
        description = "we are heading right"
    logging.debug("It took %s seconds to determine that %s." %(delay, description))

    # delay is the amount of time that the game has been moving
    # before we try to take control
    # s = (SQUARE_SIZE + delay) / 2
    s = delay * 1.3 # this magic number was found by trial and error

    if playerDirection == "4d" or playerDirection == "d":
        i = 0
        while i < 3: # repeat a few times just to be safe
            movePlayer('left', s)
            movePlayer('up', s)
            movePlayer('right', s * 0.8) # prevents new open paths
            movePlayer('down', s * 0.8)  # with the added benefit that we
                                         # end up moving up and left
            i = i + 1

    elif playerDirection == "3l" or playerDirection == "l":
        i = 0
        while i < 3: # repeat a few times just to be safe
            movePlayer('up', s)
            movePlayer('right', s)
            movePlayer('down', s * 0.8)  # prevents new open paths
            movePlayer('left', s * 0.8)  # with the added benefit that we
                                         # end up moving up and right
            i = i + 1

    elif playerDirection == "2u" or playerDirection == "u":
        i = 0
        while i < 3: # repeat a few times just to be safe
            movePlayer('right', s)
            movePlayer('down', s)
            movePlayer('left', s * 0.8)  # prevents new open paths
            movePlayer('up', s * 0.8)    # with the added benefit that we
                                         # end up moving down and right
            i = i + 1

    elif playerDirection == "1r" or playerDirection == "r":
        i = 0
        while i < 3: # repeat a few times just to be safe
            movePlayer('down', s)
            movePlayer('left', s)
            movePlayer('up', s * 0.8)    # prevents new open paths
            movePlayer('right', s * 0.8) # with the added benefit that we
                                         # end up moving down and left
            i = i + 1

    elif playerDirection == "1u":
        i = 0
        while i < 3: # repeat a few times just to be safe
            movePlayer('left', s)
            movePlayer('down', s)
            movePlayer('right', s * 0.8) # prevents new open paths
            movePlayer('up', s * 0.8)    # with the added benefit that we
                                         # end up moving down and left
            i = i + 1

    elif playerDirection == "4r":
        i = 0
        while i < 3: # repeat a few times just to be safe
            movePlayer('up', s)
            movePlayer('left', s)
            movePlayer('down', s * 0.8)  # prevents new open paths
            movePlayer('right', s * 0.8) # with the added benefit that we
                                         # end up moving up and left
            i = i + 1

    elif playerDirection == "3d":
        i = 0
        while i < 3: # repeat a few times just to be safe
            movePlayer('right', s)
            movePlayer('up', s)
            movePlayer('left', s * 0.8)  # prevents new open paths
            movePlayer('down', s * 0.8)  # with the added benefit that we
                                         # end up moving up and right
            i = i + 1

    elif playerDirection == "2l":
        i = 0
        while i < 3: # repeat a few times just to be safe
            movePlayer('down', s)
            movePlayer('right', s)
            movePlayer('up', s * 0.8)    # prevents new open paths
            movePlayer('left', s * 0.8)  # with the added benefit that we
                                          # end up moving down and right
            i = i + 1

    # we further expand our safety zone
    buildSquares(s * 0.5) # this magic number was found by trial and error

# build 4 squares at the starting point in the game
def buildSquares(square_size):
    # make each square slightly bigger
    enlarge = 1.1

    movePlayer('right', square_size * enlarge)
    movePlayer('down', square_size * enlarge)
    movePlayer('left', square_size * enlarge)
    movePlayer('up', square_size * enlarge)
    
    movePlayer('up', square_size * enlarge)
    movePlayer('left', square_size * enlarge)
    movePlayer('down', square_size * enlarge)
    movePlayer('right', square_size * enlarge)
    
    movePlayer('right', square_size * enlarge)
    movePlayer('up', square_size * enlarge)
    movePlayer('left', square_size * enlarge)
    movePlayer('down', square_size * enlarge)
    
    movePlayer('down', square_size * enlarge)
    movePlayer('left', square_size * enlarge)
    movePlayer('up', square_size * enlarge)
    movePlayer('right', square_size * enlarge)
    
    # move around the 4 squares to close up any gaps
    
    movePlayer('down', square_size)
    movePlayer('left', square_size)
    movePlayer('up', square_size * 2)
    movePlayer('right', square_size * 2)
    movePlayer('down', square_size * 2)
    movePlayer('left', square_size * 2)
    movePlayer('up', square_size)
    movePlayer('right', square_size)

def spiralEdge(level, direction, square_size):
    counter = 1
    while counter < level * 2:
        buildSquares(square_size)
        movePlayer(direction, square_size)
        counter = counter + 1

    buildSquares(square_size)

if __name__ == "__main__":
    main()
