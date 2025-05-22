# XCom mini version

from __future__ import division

from copy import deepcopy
#import mcts
import cachedmctstd



class XCom():

            
    def __init__(self):

        size = self.Size = 6
        expanded = self.Expanded = 5
        self.Move = 3
        self.MaxTurns = 20
        self.Turns = 0
        
        self.board = [ [0] * size for _ in range(size)]
        self.board[2][1] = -2  # -2 is a wall
        self.board[2][4] = -2
        self.board[3][1] = -2
        self.board[3][4] = -2
        self.board[3][2] = -2
        self.board[2][3] = -2
        self.board[0][2] = 1   # 1 is human
        self.board[0][3] = 1
        
        self.board[5][2] = -1   # -1 is alien
        self.board[5][3] = -1
        
        self.currentPlayer = 1
        
        self.boardExpanded = [ [0] * size * expanded for _ in range(size * expanded)]
        for row in range(size*expanded):
            for col in range(size*expanded):                
                if self.board[row//expanded][col//expanded] == -2:                    
                    self.boardExpanded[row][col] = -2
        
        #for row in range(size):
        #    for col in range(size):
        #        if self.board[row][col] == 1:
        #            self.boardExpanded[self.convCoord(row)][self.convCoord(col)] = 1
        #        elif self.board[row][col] == -1:
        #            self.boardExpanded[self.convCoord(row)][self.convCoord(col)] = -1


        #print(self.lineTrace(2,0,5,1))
        self.showExpandedBoard()
        self.showBoard()
        
        #print(self.getPossibleActions())


    def convCoord(self, x1):
        return x1 * self.Expanded + self.Expanded // 2
    
    
    def showBoard(self):
        for row in self.board:
            for col in row:
                if col == 0:
                    print('-', end='')
                elif col == 1:
                    print('H', end='')
                elif col == -1:
                    print('A', end='')
                elif col == -2:
                    print('O', end='')                    
                else:
                    print('X', end='') #error
            print('')
    
    def showExpandedBoard(self):
        for row in self.boardExpanded:
            for col in row:
                if col == 0:
                    print('-', end='')
                elif col == 1:
                    print('H', end='')
                elif col == -1:
                    print('A', end='')
                elif col == 3:
                    print('R', end='')                        
                elif col == -2:
                    print('O', end='')
                else:
                    print('X', end='') #error
            print('')
    
    # returns true if there are no obstacles between (x1,y1) and (x2,y2)
    def lineTrace(self, x1, y1, x2, y2):
                
        expanded = self.Expanded
        size = self.Size
        
        if (abs(x2-x1) >= abs(y2-y1)):
                
            if x2 < x1:  # ensure x1 is always smaller
                temp = x1
                x1 = x2
                x2 = temp
                temp = y1
                y1 = y2
                y2 = temp
                
            x1 = self.convCoord(x1)
            y1 = self.convCoord(y1)
            x2 = self.convCoord(x2)
            y2 = self.convCoord(y2)
            
            if x1 != x2:
                slope = (y2-y1)/(x2-x1)
            else:
                slope = 100000
                    
            xCurr = x1
            yCurr = y1
            
            while xCurr <= x2:            
                
                if self.boardExpanded[int(xCurr)][int(yCurr)] != 0:
                    if (int(xCurr) != x1 or int(yCurr) != y1) and (int(xCurr) != x2 or int(yCurr) != y2):
                        return False
                #self.boardExpanded[int(xCurr)][int(yCurr)] = 3
                    
                xCurr = xCurr + 1
                yCurr = yCurr + slope
                if yCurr >= expanded * size or yCurr < 0:
                    break
        else:
            
            if y2 < y1:  # ensure y1 is always smaller
                temp = x1
                x1 = x2
                x2 = temp
                temp = y1
                y1 = y2
                y2 = temp
                
            x1 = self.convCoord(x1)
            y1 = self.convCoord(y1)
            x2 = self.convCoord(x2)
            y2 = self.convCoord(y2)
            
            if y1 != y2:
                slope = (x2-x1)/(y2-y1)
            else:
                slope = 100000
                    
            xCurr = x1
            yCurr = y1
            
            while yCurr <= y2:            
                
                if self.boardExpanded[int(xCurr)][int(yCurr)] != 0:
                    if (int(xCurr) != x1 or int(yCurr) != y1) and (int(xCurr) != x2 or int(yCurr) != y2):
                        return False
                #self.boardExpanded[int(xCurr)][int(yCurr)] = 3
                
                yCurr = yCurr + 1
                xCurr = xCurr + slope
                if xCurr >= expanded * size or xCurr < 0:
                    break
                    
        return True
        
    def getCurrentPlayer(self):
        return self.currentPlayer

    def getPossibleActions(self):
        possibleActions = []
        seenActions = set()
        
        myPlayers = []
        oppoPlayers = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                
                if self.currentPlayer == 1:
                    if self.board[i][j] == 1:
                        myPlayers.append((i,j))
                    elif self.board[i][j] == -1:
                        oppoPlayers.append((i,j))
                elif self.currentPlayer == -1:
                    if self.board[i][j] == -1:
                        myPlayers.append((i,j))
                    elif self.board[i][j] == 1:
                        oppoPlayers.append((i,j))
                        
        #shoot
        for i in myPlayers:
            for j in oppoPlayers:             
                if self.lineTrace(i[0], i[1], j[0], j[1]):
                    possibleActions.append(Action(self.currentPlayer, i[0], i[1], i[0], i[1], j[0], j[1], 'shoot'))
                
        #move
        for i in myPlayers:
            self.recursiveMove(possibleActions, seenActions, i[0], i[1], i[0], i[1], oppoPlayers, 0)


        if possibleActions == []:  # error
            print('No Possible Actions Error')   
            self.showBoard()
        
        return possibleActions

    # depth-first recursive function to find all possible moves
    def recursiveMove(self, possibleActions, seenActions, currX, currY, oriX, oriY, oppoPlayers, step):
        
        if step >= self.Move:
            return
        
        for row, col in [(0,-1), (-1,0), (1,0), (0,1)]:
                destX = currX + row
                destY = currY + col
                if destX >= 0 and destX < self.Size and destY >= 0 and destY < self.Size:
                    if abs(row) + abs(col) <= 1 and self.board[destX][destY] == 0:  #can move
                        canShoot = False
                        for j in oppoPlayers:             
                            if self.lineTrace(destX, destY, j[0], j[1]):
                                act = Action(self.currentPlayer, oriX, oriY, destX, destY, j[0], j[1], 'shoot')
                                if act not in seenActions:
                                    possibleActions.append(act)
                                    seenActions.add(act)
                                canShoot = True
                                    
                        if not canShoot:
                            act = Action(self.currentPlayer, oriX, oriY, destX, destY, -2, -2, 'move')
                            if act not in seenActions:
                                possibleActions.append(act)
                                seenActions.add(act)
                        
                        self.recursiveMove(possibleActions, seenActions, destX, destY, oriX, oriY, oppoPlayers, step+1)
    
        
    def takeAction(self, action):
        newState = deepcopy(self)
        
        if action.action == 'move':
            newState.board[action.x1][action.y1] = 0
            newState.board[action.xDest][action.yDest] = action.player
        elif action.action == 'shoot':
            newState.board[action.x1][action.y1] = 0
            newState.board[action.xDest][action.yDest] = action.player
            newState.board[action.xTar][action.yTar] = 0
        
        newState.currentPlayer = self.currentPlayer * -1
        newState.Turns += 1
        
        return newState

    def isTerminal(self):
        
        if self.Turns > self.MaxTurns:
            return True
        
        myPlayers = False
        oppoPlayers = False
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                
                if self.board[i][j] == 1:
                    myPlayers = True
                elif self.board[i][j] == -1:
                    oppoPlayers = True
        
        return (not myPlayers) or (not oppoPlayers)
        

    def getReward(self):
        myPlayers = 0
        oppoPlayers = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                
                if self.board[i][j] == 1:
                    myPlayers += 1
                elif self.board[i][j] == -1:
                    oppoPlayers += 1
        
        if myPlayers == 0:
            return oppoPlayers * -10
        elif oppoPlayers == 0:
            return myPlayers * 10            
        elif self.Turns > self.MaxTurns:            
            return 0
        else:
            print("Reward Error")
        return False

    
    def calculatePos(self):
        myPlayers = 0
        oppoPlayers = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                
                if self.board[i][j] == 1:
                    myPlayers += 1
                elif self.board[i][j] == -1:
                    oppoPlayers += 1
        
        return myPlayers-oppoPlayers

class Action():
    # Current (x,y) -> Destination (x,y) -> Shoot at Target (x,y)
    def __init__(self, player, x1, y1, xDest, yDest, xTar, yTar, act):
        self.player = player
        self.x1 = x1
        self.y1 = y1
        self.xDest = xDest
        self.yDest = yDest
        self.xTar = xTar
        self.yTar = yTar
        self.action = act

    def __str__(self):
        return str((self.x1, self.y1, self.xDest, self.yDest, self.xTar, self.yTar, self.action))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.x1 == other.x1 and self.y1 == other.y1 and self.xDest == other.xDest and self.yDest == other.yDest and self.xTar == other.xTar and self.yTar == other.yTar and self.player == other.player

    def __hash__(self):
        return hash((self.x1, self.y1, self.xDest, self.yDest, self.xTar, self.yTar, self.player))


if __name__=="__main__":
   
    # run experiments
    

    searcher = cachedmctstd.cachedmctstd(iterationLimit=100)
    #searcher2 = mcts.mcts(iterationLimit=100)
    
    s1wins = 0
    s2wins = 0
    draws = 0

    
    for rounds in range(0,50):
    
        print("Round:", rounds)
        state = XCom()
         
        for turn in range(1,20):
        
            # human player    
        
            if rounds % 2 == 1 and turn == 1: # two players alternate starting first
                action = Action(state.currentPlayer, 0, 2, 0, 2, -1, -1, 'move')
                print(action)
                #reward = 0
            else:
                actionPkg = searcher.search(initialState=state, needDetails=True)
                print(actionPkg)    
                action = actionPkg.get('action')
                mcts_reward = actionPkg.get('expectedReward')
            
                f = open("exp-mctstd-fixed1-reward.csv", "a")
                f.write("Reward," + str(mcts_reward))
                f.write('\n')            
                f.close()
            
            xCoor = action.x1
            yCoor = action.y1
            
            curStateString = ''            
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    
                    xCurr = xCoor +i
                    yCurr = yCoor +j
                    
                    if xCurr >= 0 and xCurr < state.Size and yCurr >=0 and yCurr < state.Size:
                        if state.board[xCurr][yCurr] == 0:
                            curStateString += '0'
                        elif state.board[xCurr][yCurr] == -2:
                            curStateString += '1'
                        else:
                            curStateString += '0'
                    else:
                        curStateString += '1'    
             
            curPos = state.calculatePos()
             
            state = state.takeAction(action)
            state.showBoard()
            
            reward = (state.calculatePos() - curPos) * 10
            
            xCoor = action.xDest
            yCoor = action.yDest
            
            nextStateString = ''            
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    
                    xCurr = xCoor +i
                    yCurr = yCoor +j
                    
                    if xCurr >= 0 and xCurr < state.Size and yCurr >=0 and yCurr < state.Size:
                        if state.board[xCurr][yCurr] == 0:
                            nextStateString += '0'
                        elif state.board[xCurr][yCurr] == -2:
                            nextStateString += '1'
                        else:
                            nextStateString += '0'
                    else:
                        nextStateString += '1'                                  
            
            searcher.update(curStateString, nextStateString, reward)
            searcher.showStates()
            
            if state.isTerminal():
                break
        
            
            # alien player

            curPos = state.calculatePos()
            
        
            possibleActions  = state.getPossibleActions()
            
            action = possibleActions[0]
            print(action)
            
            state= state.takeAction(action)
            state.showBoard()
            
            reward = (state.calculatePos() - curPos) * 10
            
            
        
            searcher.update(nextStateString, nextStateString, reward)
            searcher.showStates()
            
            if state.isTerminal():
                break
        
        if state.getReward() > 0:
            s1wins += 1
        elif state.getReward() < 0:
            s2wins += 1
        else:
            draws += 1
        
    
    
        print("Human wins:", s1wins)
        print("Alien wins:", s2wins)
        print("Draws:", draws)
        
    
        
        if rounds % 10 == 9:
            
            f = open("exp-cachedmctstd-fixed1.csv", "a")
            f.write("Human wins," + str(s1wins) + "," + "Alien wins," + str(s2wins) + "," + "Draws," + str(draws))
            f.write('\n')
            s1wins = 0
            s2wins = 0
            draws = 0
        
            f.close()

            f = open("exp-cachedmctstd-fixed1-reward.csv", "a")
            f.write("Done")
            f.write('\n')            
            f.close()