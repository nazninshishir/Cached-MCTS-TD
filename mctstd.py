# MCTS with Temporal Difference Learning, with MCTS adapted from @pbsinclair42 

from __future__ import division

import time
import math
import random


def randomPolicy(state):
    while not state.isTerminal():
        try:
            action = random.choice(state.getPossibleActions())
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.takeAction(action)
    return state.getReward()


class treeNode():
    def __init__(self, state, parent, action):
        self.state = state
        self.isTerminal = state.isTerminal()
        self.isFullyExpanded = self.isTerminal
        self.parent = parent
        self.action = action
        self.numVisits = 0
        self.totalReward = 0
        self.children = {}    # map {action, newNode}

    def __str__(self):
        s=[]
        s.append("totalReward: %s"%(self.totalReward))
        s.append("numVisits: %d"%(self.numVisits))
        s.append("isTerminal: %s"%(self.isTerminal))
        s.append("possibleActions: %s"%(self.children.keys()))
        return "%s: {%s}"%(self.__class__.__name__, ', '.join(s))

class mctstd():
    def __init__(self, timeLimit=None, iterationLimit=None, explorationConstant=1 / math.sqrt(2),
                 rolloutPolicy=randomPolicy):
        
        self.states = {}
        self.alpha = 0.8
        self.gamma = 0.0
        
        
        if timeLimit != None:
            if iterationLimit != None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
            if iterationLimit == None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iterationLimit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.searchLimit = iterationLimit
            self.limitType = 'iterations'
        self.explorationConstant = explorationConstant
        self.rollout = rolloutPolicy

    def search(self, initialState, needDetails=False):
        
        self.player = initialState.getCurrentPlayer()
        
        self.root = treeNode(initialState, None, None)

        if self.limitType == 'time':
            timeLimit = time.time() + self.timeLimit / 1000
            while time.time() < timeLimit:
                self.executeRound()
        else:
            for i in range(self.searchLimit):
                self.executeRound()

        bestChild = self.getBestChild(self.root, 0)
        action=(action for action, node in self.root.children.items() if node is bestChild).__next__()
                
        
        if needDetails:
            return {"action": action, "expectedReward": bestChild.totalReward / bestChild.numVisits}
        else:
            return action

    def executeRound(self):
        """
            execute a selection-expansion-simulation-backpropagation round
        """
        node = self.selectNode(self.root)
        reward = self.rollout(node.state)  * self.player
        self.backpropogate(node, reward)

    def selectNode(self, node):
        while not node.isTerminal:
            if node.isFullyExpanded:
                node = self.getBestChild(node, self.explorationConstant)
            else:
                return self.expand(node)
        return node

    def expand(self, node):
        actions = node.state.getPossibleActions()
        for action in actions:
            if action not in node.children:
                newNode = treeNode(node.state.takeAction(action), node, action)
                node.children[action] = newNode
                if len(actions) == len(node.children):
                    node.isFullyExpanded = True
                return newNode

        raise Exception("Should never reach here")

    def backpropogate(self, node, reward):
        while node is not None:
            node.numVisits += 1
            node.totalReward += reward
            reward = -1 * reward
            node = node.parent

    def getBestChild(self, node, explorationValue):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
                        
            
            if node.state.getCurrentPlayer() == 1 and child.action.action =='move':
                
                xCoor = child.action.xDest
                yCoor = child.action.yDest
                
                curStateString = ''            
                for i in [-1,0,1]:
                    for j in [-1,0,1]:
                        
                        xCurr = xCoor +i
                        yCurr = yCoor +j
                        
                        if xCurr >= 0 and xCurr < child.state.Size and yCurr >=0 and yCurr < child.state.Size:
                            if child.state.board[xCurr][yCurr] == 0:
                                curStateString += '0'
                            elif child.state.board[xCurr][yCurr] == -2:
                                curStateString += '1'
                            else:
                                curStateString += '0'
                        else:
                            curStateString += '1'    
                
                if curStateString in self.states:
                    stateValue = self.states[curStateString]
                else:
                    stateValue = 0
            else:
                stateValue = 0
            
            nodeValue = child.totalReward / child.numVisits + explorationValue * math.sqrt(
                2 * math.log(node.numVisits) / child.numVisits) + stateValue
            
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        
        return random.choice(bestNodes)
    
    
    def update(self, curStateString, nextStateString, reward):
        
        if not (nextStateString in self.states):
            self.states[nextStateString] = 0.0
            
        if curStateString in self.states:
            self.states[curStateString] = self.states[curStateString] + self.alpha * (reward + self.gamma * self.states[nextStateString] - self.states[curStateString])
        else:
            self.states[curStateString] = self.alpha * (reward + self.gamma * self.states[nextStateString])
    
    def showStates(self):
        for key in self.states:
            print(key, '->', self.states[key])
            