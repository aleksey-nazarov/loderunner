import msvcrt
from loderunnerclient.internals.actions import LoderunnerAction

class ManualControl:
    def getAction(self, gcb):
        print(gcb.get_my_position())
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if ( key == b'w' ):
                return LoderunnerAction.GO_UP
            if ( key == b'a' ):
                return LoderunnerAction.GO_LEFT
            if ( key == b's' ):
                return LoderunnerAction.GO_DOWN
            if ( key == b'd' ):
                return LoderunnerAction.GO_RIGHT
            if ( key == b'z' ):
                return LoderunnerAction.DRILL_LEFT
            if ( key == b'x' ):
                return LoderunnerAction.DRILL_RIGHT
        return LoderunnerAction.DO_NOTHING


