from loderunnerclient.LodeRunnerClient import GameClient
import random
import logging

from loderunnerclient.internals.actions import LoderunnerAction
from loderunnerclient.internals.board import Board

from decider import Decider
from manual_control import ManualControl # REMOVE
import pickle

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.INFO)

decisionMaker = Decider()
manualControl = ManualControl() # REMOVE

def turn(gcb: Board):
    #action_id = random.randint(0, len(LoderunnerAction)-1)
    #return list(LoderunnerAction)[action_id]

    try:
        return decisionMaker.getDecision(gcb)
    except Exception as e:
        with open('error_gcb', 'wb') as f:
            pickle.dump(gcb, f)
        exit()

    #return decisionMaker.getDecision(gcb)
    #return manualControl.getAction(gcb) # REMOVE

if __name__ == '__main__':
    #gcb = GameClient("localhost:8080", "<player-id>", "<code>")
    #http://codingdojo2019.westeurope.cloudapp.azure.com/codenjoy-contest/board/player/wm17l2vo79u944kteg76?code=7697831377508766095&gameName=loderunner
    gcb = GameClient("codingdojo2019.westeurope.cloudapp.azure.com:80", "wm17l2vo79u944kteg76", "7697831377508766095")
    gcb.run(turn)
