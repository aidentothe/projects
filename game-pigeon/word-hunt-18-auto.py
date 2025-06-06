# from pynput.keyboard import Listener
import pyautogui
from pynput.mouse import Button, Controller
import subprocess
import time
import re
import numpy
# import pytesseract
import cv2
from PIL import ImageGrab
import easyocr

# Construct trie from wordlist

mouse = Controller()

print("Constructing Trie...")


def char_to_ind(c):
    return ord(c) - ord('A')


class Node:
    def __init__(self):
        self.is_word = False
        self.children = [-1 for i in range(26)]


trie = [Node()]

wordlist1 = open("words.txt", "r")
wordlist2 = open("english.txt", "r")

wordlist = []

for word in wordlist1:
    wordlist.append(word)
for word in wordlist2:
    wordlist.append(word)

for word in wordlist:
    word = word[:-1].upper()
    word = re.sub(r'\W+', '', word)

    if len(word) < 3:
        continue
    index = 0
    for char in word:
        if ord(char) == 10:
            break
        if trie[index].children[char_to_ind(char)] == -1:
            trie[index].children[char_to_ind(char)] = len(trie)
            index = len(trie)
            trie.append(Node())
        else:
            index = trie[index].children[char_to_ind(char)]
    trie[index].is_word = True

# Mouse movement


def moveMouse(dx, dy):
    mouse.move(dx, dy)
    time.sleep(0.02)


def mouseDown():
    mouse.press(Button.left)
    time.sleep(0.02)


def mouseUp():
    mouse.release(Button.left)
    time.sleep(0.02)


def homeCursor():
    mouse.position = (1050, 486)
    time.sleep(0.02)


def evalWord(w):
    l = len(w)
    if l < 3:
        return 0
    elif l == 3:
        return 100
    elif l == 4:
        return 400
    elif l == 5:
        return 800
    elif l == 6:
        return 1400
    elif l == 7:
        return 1800
    elif l == 8:
        return 2200
    else:
        return 2600


reader = easyocr.Reader(['en'])

while True:
    print("Start?")
    input()

    cmd = 'osascript -e \'activate application "iPhone Mirroring"\''
    subprocess.call(cmd, shell=True)

    mouse.position = (1138, 628)
    time.sleep(0.02)
    mouseDown()
    time.sleep(0.1)
    mouseUp()

    time.sleep(2)

    left = 1022
    right = 1192
    top = 458
    bottom = 628

    width = 56
    height = 56

    board = [['T', 'E', 'S', 'T'], ['T', 'E', 'S', 'T'],
             ['T', 'E', 'S', 'T'], ['T', 'E', 'S', 'T']]
    board_width = 4
    board_height = 4

    print("Scanning Board...\n")

    i = 0
    for x in range(left, right+1, int((right - left)/3)):
        j = 0
        for y in range(top, bottom+1, int((bottom - top)/3)):
            boardImage = cv2.resize(cv2.bitwise_not(cv2.cvtColor(
                numpy.array(ImageGrab.grab(bbox=(x+7, y+7, x + width-7, y + height-7))), cv2.COLOR_BGR2GRAY)), (300, 300))
            thresh = cv2.threshold(boardImage, 150, 255,
                                   cv2.THRESH_BINARY_INV)[1]
            result = cv2.GaussianBlur(thresh, (5, 5), 0)
            # boardText = pytesseract.image_to_string(
            #     result, lang='eng', config='--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            text = reader.recognize(result, detail=0)
            board[j][i] = text[0].upper()
            if board[j][i] == "0":
                board[j][i] = 'O'
            if board[j][i] == '|' or board[j][i] == ']' or board[j][i] == '[' or board[j][i] == '1':
                board[j][i] = 'I'
            if board[j][i] == '5':
                board[j][i] = 'S'

            # print(text)
            # cv2.imshow('frame', result)
            # cv2.waitKey(4)
            # cv2.destroyAllWindows()
            j = j+1
        i = i+1

    print(board)

    # Generate paths

    mx = [-1, 0, 1, 1, 1, 0, -1, -1]
    my = [-1, -1, -1, 0, 1, 1, 1, 0]

    vis = [[False for i in range(4)] for j in range(4)]
    found_words = {}
    found_paths = []
    expected_score = 0

    def dfs(x, y, index, path, word):
        global expected_score
        vis[y][x] = True
        if trie[index].is_word and (not (word in found_words)) and len(word) > 2:
            found_words[word] = True
            found_paths.append((path.copy(), word))
            expected_score = expected_score + evalWord(word)
        for mv in range(8):
            nx = x + mx[mv]
            ny = y + my[mv]
            # print(board[ny][nx], trie[index].children[char_to_ind(board[ny][nx])])
            if nx < 0 or nx >= board_width or ny < 0 or ny >= board_height or trie[index].children[char_to_ind(board[ny][nx])] == -1 or vis[ny][nx]:
                continue
            path.append((nx, ny))
            dfs(nx, ny, trie[index].children[char_to_ind(
                board[ny][nx])], path, word + board[ny][nx])
            path.pop()
        vis[y][x] = False

    print("Finding Paths...")
    for x in range(board_width):
        for y in range(board_height):
            path = [(x, y)]
            dfs(x, y, trie[0].children[char_to_ind(
                board[y][x])], path, board[y][x])

    found_paths = sorted(found_paths, key=lambda x: len(x[1]))
    found_paths.reverse()

    # Follow paths

    strLen = 56
    diagLen = 56

    def gotoAdjCell(cx, cy, x, y):
        if x == cx and y == cy:
            return
        if x == cx:
            if cy > y:
                moveMouse(0, -strLen)
            else:
                moveMouse(0, strLen)
        elif y == cy:
            if cx > x:
                moveMouse(-strLen, 0)
            else:
                moveMouse(strLen, 0)
        else:
            if cx > x and cy > y:
                moveMouse(-diagLen, -diagLen)
            elif cx > x and cy < y:
                moveMouse(-diagLen, diagLen)
            elif cx < x and cy > y:
                moveMouse(diagLen, -diagLen)
            elif cx < x and cy < y:
                moveMouse(diagLen, diagLen)

    def gotoCell(cx, cy, x, y):
        while cx < x:
            moveMouse(strLen, 0)
            cx = cx+1
        while cx > x:
            moveMouse(-strLen, 0)
            cx = cx-1
        while cy < y:
            moveMouse(0, strLen)
            cy = cy+1
        while cy > y:
            moveMouse(0, -strLen)
            cy = cy-1

    ccx = 0
    ccy = 0

    def followPath(path):
        global ccx
        global ccy
        # homeCursor()
        # for _ in range(2):
        #     moveMouse(0, 100)

        # moveMouse(0, 40)
        # moveMouse(53, 0)
        (cx, cy) = path[0]
        gotoCell(ccx, ccy, cx, cy)
        # # time.sleep(1)
        diags = []
        mouseDown()
        for (x, y) in path[1:]:
            gotoAdjCell(cx, cy, x, y)
            if cx != x and cy != y:
                diags.append((cx-x, cy-y))
            cx = x
            cy = y
        mouseUp()

        for (x, y) in reversed(diags):
            if x == -1 and cx == 0:
                gotoAdjCell(cx, cy, cx+1, cy)
                cx = cx+1
            elif x == 1 and cx == 3:
                gotoAdjCell(cx, cy, cx-1, cy)
                cx = cx-1
            if y == -1 and cy == 0:
                gotoAdjCell(cx, cy, cx, cy+1)
                cy = cy+1
            elif y == 1 and cy == 3:
                gotoAdjCell(cx, cy, cx, cy-1)
                cy = cy-1
            gotoAdjCell(cx, cy, cx+x, cy+y)
            cx = cx + x
            cy = cy + y
            # time.sleep(1)
        ccx = cx
        ccy = cy

    homeCursor()

    initial_time = time.time()
    print("Expected Score: " + str(expected_score))
    # if expected_score < 200000:
    #     print("Skipping because too low")
    #     continue
    print("Following Paths...")
    finished = True
    for path in range(len(found_paths)):
        print(found_paths[path][1])
        followPath(found_paths[path][0])
        if time.time() - initial_time > 70:
            finished = False
            break
    if finished:
        print("Done - All words!")
    else:
        print("Done - Time!")

    break
