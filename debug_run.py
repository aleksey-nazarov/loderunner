import pickle
import copy
import time
from decider import Decider

frameChangeInterval = 0.5

def setChar(x, y, char, gcb):
    s = gcb._string
    pos = gcb._xy2strpos(x, y)
    newS = s[:pos] + char + s[pos+1:]
    gcb._string = newS

def displayPath(gcb, hPath):
    gcbPath = copy.copy(gcb)
    for pt in hPath:
            setChar(*pt, '+', gcbPath)
    while(True):
        gcb.print_board()
        time.sleep(frameChangeInterval)
        gcbPath.print_board()
        time.sleep(frameChangeInterval)
    

decisionMaker = Decider()

with open('last_gcb_1', 'rb') as f:
    gcb = pickle.load(f)


# убираем золото, которое алгоритм уже нашел
##setChar(12, 24, ' ', gcb)
##setChar(6, 24, ' ', gcb)
##setChar(24, 22, ' ', gcb)
##setChar(28, 23, ' ', gcb)

gcb.print_board()
#print(gcb.get_my_position()) 6,38
#time.sleep(8)

#displayPath(gcb, [])

hPathList = []
tStart = time.time()
d = decisionMaker.getDecision(gcb, hPathList)

setChar(55, 43, '█', gcb)
gcb.print_board()

tRun = time.time() - tStart

displayPath(gcb, hPathList[0])
