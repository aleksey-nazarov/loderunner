from loderunnerclient.internals.actions import LoderunnerAction
from loderunnerclient.internals.board import Board
from loderunnerclient.internals.element import Element

goldValue = { 'YELLOW_GOLD' : 2,
              'GREEN_GOLD' : 5,
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
               Element('ENEMY_PIT') ]  # TODO возможно

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
                  Element('HERO_SHADOW_DRILL_RIGHT') ]

possibleFreeTiles = realFreeTiles + \
                    [ Element('NONE'),
                      Element('ENEMY_LEFT'),
                      Element('ENEMY_RIGHT'),
                      Element('OTHER_HERO_LEFT'),
                      Element('OTHER_HERO_RIGHT'),
                      Element('OTHER_HERO_SHADOW_LEFT'),
                      Element('OTHER_HERO_SHADOW_RIGHT') ]

                   

class Decider:
    def __init__(self):
        self._gcb = None
        pass


    def getDecision(self, gcb: Board):
        self._gcb = gcb
        heroLocation = self._gcb.get_my_position()
        hX = heroLocation.get_x()
        hY = heroLocation.get_y()
        hPath = self.getPath(hX, hY)
        print('FOUND', hPath)
        fromPt = hPath[0]
        toPt = hPath[1]
        commandList = actionToMove(*fromPt, *toPt)
        return commandList[0]


    def getPath(self, x, y, possible = False):
        """
        Ищет путь от (x, y) до ближайшего золота
        Возвращает только один путь!
        """
        hPaths = [ [ (x, y) ] ] # hPath = hero path, чтоб случайно не попутать с модулем path
        counter = 0
        while(True):
            newHPaths = []
            for hPath in hPaths:
                lastPt = hPath[-1]
                reachablePts = self.reachablePointsFrom(*lastPt)
                if ( (11,23) in hPath ):
                    print('hPath', hPath)
                #print('lastPt', lastPt)
                #print('rpts', reachablePts)
                for rpt in reachablePts:
                    if ( rpt in hPath ):
                        continue # ни шагу назат!
                    newHPaths.append( hPath + [rpt] )
                    rTile = self._gcb.get_at(*rpt)
                    if ( rTile in gold ):
                        return hPath + [rpt]
            if ( counter % 10 == 0 ):
                print(counter)
                #print(hPaths)
            #print(counter)
            counter += 1
            
            hPaths = newHPaths


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
            #pipes = possiblePipes
            freeTiles = possibleFreeTiles
            destructibleGround = possibleDestructibleGround
        else:
            ladders = realLadders
            #pipes = realPipes
            freeTiles = realFreeTiles
            destructibleGround = realDestructibleGround
        #laddersNPipes = ladders + pipes
            
        if ( fromX == toX and # tile "to" above "from"
             fromY - toY == 1 and 
             self._gcb.get_at(fromX, fromY) in ladders and # 'from' is ladder
             ( toTile in ladders or
               toTile in freeTiles ) ):
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
                return LoderunnerAction.GO_DOWN
            if ( tile in freeTiles ):
                return LoderunnerAction.DO_NOTHING # falling
            
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













