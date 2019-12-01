import pickle
from decider import Decider

decisionMaker = Decider()

with open('gcb1', 'rb') as f:
    gcb = pickle.load(f)

gcb.print_board()

d = decisionMaker.getDecision(gcb)
