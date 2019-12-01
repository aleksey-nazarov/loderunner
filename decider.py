import time
import atexit
import os.path
import pickle
from math import sqrt

from loderunnerclient.internals.actions import LoderunnerAction
from loderunnerclient.internals.board import Board
from loderunnerclient.internals.element import Element

# 1. сохранение и продолжение поиска
# 2. приоритетные действия - убегание от роботов (даже если не успевает завершить поиск)

# не имеет особого смысла, т.к. ценность золота меняется при последовательном подборе
goldValue = { 'YELLOW_GOLD' : 2,
              'GREEN_GOLD' : 7, 
              'RED_GOLD' : 10 }
# Element(''),

gold = [ Element(g) for g in goldValue.keys() ]

realLadders = [ Element('LADDER'),
                Element('HERO_LADDER'),
                Element('HERO_SHADOW_LADDER') ]

possibleLadders = realLadders + \
                  [ Element('ENEMY_LADDER'),
                    Element('OTHER_HERO_LADDER'),
                    Element('OTHER_HERO_SHADOW_LADDER') ]

realPipes = [ Element('PIPE'),
              Element('HERO_PIPE_LEFT'),
              Element('HERO_PIPE_RIGHT'),
              Element('HERO_SHADOW_PIPE_LEFT'),
              Element('HERO_SHADOW_PIPE_RIGHT') ]

possiblePipes = realPipes + \
                [ Element('ENEMY_PIPE_LEFT'),
                  Element('ENEMY_PIPE_RIGHT'),
                  Element('OTHER_HERO_PIPE_LEFT'),
                  Element('OTHER_HERO_PIPE_RIGHT'),
                  Element('OTHER_HERO_SHADOW_PIPE_LEFT'),
                  Element('OTHER_HERO_SHADOW_PIPE_RIGHT') ]

realDestructibleGround = [ Element('BRICK') ]

possibleDestructibleGround = realDestructibleGround + \
                             [ Element('PIT_FILL_1'),
                               Element('PIT_FILL_2'),
                               Element('PIT_FILL_3'),
                               Element('PIT_FILL_4'),
                               Element('DRILL_PIT') ] # TODO возможно

realGround = realDestructibleGround + \
             [ Element('UNDESTROYABLE_WALL'),
               Element('ENEMY_PIT'), # TODO возможно
               Element('HERO_PIPE_LEFT'),
               Element('HERO_PIPE_RIGHT'),
               Element('OTHER_HERO_LEFT'),
               Element('OTHER_HERO_RIGHT') ]  

possibleGround = realGround + \
                 possibleDestructibleGround
                 
realFreeTiles = gold + \
                [ Element('NONE'),
                  Element('HERO_LEFT'),
                  Element('HERO_RIGHT'),
                  Element('HERO_FALL_LEFT'),
                  Element('HERO_FALL_RIGHT'),
                  Element('HERO_SHADOW_LEFT'),
                  Element('HERO_SHADOW_RIGHT'),
                  Element('HERO_SHADOW_FALL_LEFT'),
                  Element('HERO_SHADOW_FALL_RIGHT'),
                  Element('HERO_DRILL_LEFT'),
                  Element('HERO_DRILL_RIGHT'),
                  Element('HERO_SHADOW_DRILL_LEFT'),
                  Element('HERO_SHADOW_DRILL_RIGHT'),
                  Element('DRILL_PIT') ] # POSSIBLE UNSAFE

possibleFreeTiles = realFreeTiles + \
                    [ Element('NONE'),
                      Element('ENEMY_LEFT'),
                      Element('ENEMY_RIGHT'),
                      Element('OTHER_HERO_LEFT'),
                      Element('OTHER_HERO_RIGHT'),
                      Element('OTHER_HERO_SHADOW_LEFT'),
                      Element('OTHER_HERO_SHADOW_RIGHT') ]

PATH_SEARCH_TRIES_BEFORE_SUICIDE = 15
MAX_PATH_SEARCH_TIME = 0.9

class Decider:
    def __init__(self):
        self._gcb = None
        self._pathNotFoundCount = 0
        atexit.register(self.dumpGcb)
        pass


    def getDecision(self, gcb: Board, ret=None):
        """
        ret - если в этот параметр передать пустой список, то в нем (списке) вернется найденный путь
        (сделано для отладки)
        """
        self._gcb = gcb
        heroLocation = self._gcb.get_my_position()
        hX = heroLocation.get_x()
        hY = heroLocation.get_y()
        hPath = self.getPath(hX, hY)
        #print('FOUND', hPath)
        #if ( hPath == None ): # не удалось найти
        #    return LoderunnerAction.DO_NOTHING
        if ( ret != None ):
            ret.append(hPath)
        try:
            fromPt = hPath[0]
            toPt = hPath[1]
            commandList = self.actionToMove(*fromPt, *toPt)
            cmd = commandList[0]
            self._pathNotFoundCount = 0
            return cmd
        except (TypeError, IndexError):
            print('PATH SEARCHING ERROR')
            self._pathNotFoundCount += 1
            if ( self._pathNotFoundCount > PATH_SEARCH_TRIES_BEFORE_SUICIDE ):
                return LoderunnerAction.SUICIDE
            return LoderunnerAction.DO_NOTHING


    def getPath(self, x, y, possible = False):
        """
        Ищет путь от (x, y) до ближайшего золота
        Возвращает только один путь!
        """
        hPaths = [ [ (x, y) ] ] # hPath = hero path, чтоб случайно не попутать с модулем path
        counter = 0
        startTime = time.time()
        while(True):
            newHPaths = []
            visited = []
            for hPath in hPaths:
                #print(hPath)
                runTime = time.time() - startTime
                if ( runTime > MAX_PATH_SEARCH_TIME ):
                    print('NOT found, depth {}'.format(counter))
                    return self.getApproxPath(hPaths)
                lastPt = hPath[-1]
                reachablePts = self.reachablePointsFrom(*lastPt)
                #if ( (16, 39) in hPath ):
                    #print('hPath', hPath)
                #print('hPath', hPath)
                #print('lastPt', lastPt)
                #print('rpts', reachablePts)
                for rpt in reachablePts:
                    if ( rpt in visited ):
                        continue # ни шагу назат!
                    visited.append(rpt)
                    newHPaths.append( hPath + [rpt] )
                    rTile = self._gcb.get_at(*rpt)
                    if ( rTile in gold ):
                        print('found, depth {}'.format(counter))
                        return hPath + [rpt]
            if ( counter % 10 == 0 ):
                pass
                #print(counter)
                #print(hPaths)
            #print(counter)
            counter += 1
            
            hPaths = newHPaths

            if ( newHPaths == [] ):
                return None

    def getApproxPath(self, hPaths):
        # TODO упрощенно в центр
        #print(hPaths)
        nearestGoldPos = self.getNearestGold()
        if ( nearestGoldPos != None  ):
            tgtX = nearestGoldPos[0]
            tgtY = nearestGoldPos[1] 
            print('going to nearest gold at {}, {}'.format(tgtX, tgtY))
        else:
            side = sqrt(len(self._gcb._string))
            coord = int(side / 2)
            tgtX = coord
            tgtY = coord
            print('going to center at {}, {}'.format(tgtX, tgtY))
        lastPts = []
        for hPath in hPaths:
            try:
                lastPt = hPath[-1]
                x = lastPt[0]
                y = lastPt [1]
                dist = sqrt( (tgtX - x)**2 + (tgtY - y)**2 )
                lastPts.append( (lastPt, dist, hPath) )
            except IndexError:
                continue
        lastPts.sort(key = lambda x: x[1])
        try:
            return lastPts[0][2]
        except IndexError:
            return None


    def getNearestGold(self):
        goldPoss = self._gcb.get_gold_positions()
        myPos = self._gcb.get_my_position()
        myX = myPos.get_x()
        myY = myPos.get_y()
        ratedGoldPoss = []
        for goldPos in goldPoss:
            gX = goldPos.get_x()
            gY = goldPos.get_y()
            dist = sqrt( (gX - myX)**2 + (gY - myY)**2 )
            ratedGoldPoss.append( (goldPos, dist) )
        ratedGoldPoss.sort(key = lambda x: x[1])
        try:
            return ratedGoldPoss[0][0].get_x(), ratedGoldPoss[0][0].get_y()
        except IndexError:
            return None
            


    def reachablePointsFrom(self, x, y, possible = False):
        #initialSetUpper   = [ (x-1, y-1), (x, y-1), (x+1, y-1) ]
        #initialSetLeveled = [ (x-1, y  ),           (x+1, y  ) ]
        #initialSetBelow   = [ (x-1, y+1), (x, y+1), (x+1, y+1) ]
        initialSet  = [              (x, y-1),            
                        (x-1, y  ),            (x+1, y  ), 
                        (x-1, y+1),  (x, y+1), (x+1, y+1)  ]
        
        availablePts = []
        for pt in initialSet:
            if ( self.actionToMove(x, y, *pt, possible) != None ):
                #print('dsc: ', x, y, pt, self.actionToMove(x, y, *pt, possible))
                availablePts.append(pt)

        return availablePts


    def actionToMove(self, fromX, fromY, toX, toY, possible = False):
        # вверх
        toTile = self._gcb.get_at(toX, toY)
        if ( possible == True ):
            ladders = possibleLadders
            pipes = possiblePipes
            freeTiles = possibleFreeTiles
            destructibleGround = possibleDestructibleGround
        else:
            ladders = realLadders
            pipes = realPipes
            freeTiles = realFreeTiles
            destructibleGround = realDestructibleGround
        #laddersNPipes = ladders + pipes
            
        if ( fromX == toX and # tile "to" above "from"
             fromY - toY == 1 and 
             self._gcb.get_at(fromX, fromY) in ladders and # 'from' is ladder
             ( toTile in ladders or
               toTile in freeTiles or
               toTile in pipes) ):
            return [ LoderunnerAction.GO_UP ]

        # вбок
        delta = toX - fromX
        if ( fromY == toY and # one level
             abs(delta) == 1 and # are near
             self.canHoldOn(fromX, fromY) and # can hold on "from"
             ( self.canHoldOn(toX, toY) or # toTile not occupied
               toTile in freeTiles ) ):
            if ( delta == 1):
                return [ LoderunnerAction.GO_RIGHT ]
            if ( delta == -1 ):
                return [ LoderunnerAction.GO_LEFT ]

        # вниз
        tile = self._gcb.get_at(fromX, fromY)
        if ( fromX == toX and # tile "to" below "from"
             toY - fromY == 1 and
             ( self.canHoldOn(fromX, fromY) or # hero can be on this tile
               tile in freeTiles or
               tile in possibleDestructibleGround ) and
             toTile in freeTiles ):
            if ( self.canHoldOn(fromX, fromY) ):
                return [ LoderunnerAction.GO_DOWN ]
            if ( tile in freeTiles or
                 tile in possibleDestructibleGround ):
                #return [ LoderunnerAction.DO_NOTHING ] # falling
                return [ LoderunnerAction.GO_DOWN ]
            
        # вправо-вниз и влево-вниз, в случае успеха возвращаются два действия, одно из которых - сверление
        deltaX = toX - fromX
        tileAboveToTile = self._gcb.get_at(toX, toY-1)
        if ( toY - fromY == 1 and # tile "to" below "from"
             abs(deltaX) == 1 and # one tile left or right
             toTile in destructibleGround and # theoretically can be destroyed
             tile not in possiblePipes and # cannot drill from pipes
             tileAboveToTile in freeTiles ): # above tile can be accessed
            if ( deltaX == 1 ):
                return [ LoderunnerAction.DRILL_RIGHT,
                         LoderunnerAction.GO_RIGHT]
            if ( deltaX == -1 ):
                return [ LoderunnerAction.DRILL_LEFT,
                         LoderunnerAction.GO_LEFT]
             
        
        return None # не найден вариант действий


    def canHoldOn(self, x, y, possible = False):
        """
        Можно находиться на клетке и не падать
        """
        if ( possible == True ):
            laddersNPipes = possibleLadders + possiblePipes
        else:
            laddersNPipes = realLadders + realPipes
        
        tile = self._gcb.get_at(x, y)
        if ( tile in laddersNPipes ):
            return True
        
        belowTile = self._gcb.get_at(x, y+1)
        if ( possible == True ):
            freeTiles = possibleFreeTiles
            firmFloorTiles = possibleGround + possibleLadders
        else:
            freeTiles = realFreeTiles
            firmFloorTiles = realGround + realLadders
        if ( tile in freeTiles and
             belowTile in firmFloorTiles ):
            return True

        return False


    def dumpGcb(self):
        fileName = 'last_gcb'
        fileNo = 1
        while( os.path.isfile(fileName + '_' + str(fileNo)) == True ):
            fileNo += 1
        with open(fileName + '_' + str(fileNo), 'wb') as f:
            pickle.dump(self._gcb, f)













