import random
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG
from Estimator import patternTable
from Estimator import pvalTable as valueTable
import random
from collections import defaultdict as ddict
# from example import logDebug, logTraceBack

Width = 20
Height = 20
MaxDepth = 6
branchFactor = 10

dx = (1, 0, 1, 1)
dy = (0, 1, 1, -1)  # direction vector

win = 7  # pattern
flex4 = 6
block4 = 5
flex3 = 4
block3 = 3
flex2 = 2
block2 = 1

Outside = 3
Empty = 2
Black = 1
White = 0

times = 85

class Cell:
    # Points on the board
    def __init__(self, x=0, y=0, iscand=0, piece=Empty):
        self.x = x
        self.y = y
        self.iscand = iscand  # number of neighbors within 2 blocks
        self.piece = piece  # color
        self.pattern = [[0, 0] for _ in range(4)]  # pattern
        self.value = [0, 0]  # heuristic score
        self.movevalue = 0

    def update_value(self):
        self.value[0] = valueTable[self.pattern[0][0]][self.pattern[1][0]][self.pattern[2][0]][self.pattern[3][0]]
        self.value[1] = valueTable[self.pattern[0][1]][self.pattern[1][1]][self.pattern[2][1]][self.pattern[3][1]]



class Board:
    def __init__(self):  # board
        self.width = Width
        self.height = Height
        self.board = [[Cell(x, y, 0, 2) for y in range(Height + 8)] for x in range(Width + 8)]
        self.record = []  # moves
        self.step = 0  # Chess number
        self.who = White
        self.opp = Black
        self.count_dict = ddict(lambda: 0.0)
        self.timecontrol = 0


    def init_board(self):
        # Initialize color
        for i in range(0, Height + 8):
            for j in range(0, Width + 8):
                if self.isFree(i, j):
                    self.board[i][j].piece = Empty
                else:
                    self.board[i][j].piece = Outside
        # Initialize pattern
        for i in range(4, Width + 4):
            for j in range(4, Height + 4):
                for direction in range(0, 4):
                    key = (self.board[i - 4 * dx[direction]][j - 4 * dy[direction]].piece) ^ (
                            self.board[i - 3 * dx[direction]][j - 3 * dy[direction]].piece << 2) \
                          ^ (self.board[i - 2 * dx[direction]][j - 2 * dy[direction]].piece << 4) ^ (
                                  self.board[i - dx[direction]][j - dy[direction]].piece << 6) \
                          ^ (self.board[i + dx[direction]][j + dy[direction]].piece << 8) ^ (
                                  self.board[i + 2 * dx[direction]][j + 2 * dy[direction]].piece << 10) \
                          ^ (self.board[i + 3 * dx[direction]][j + 3 * dy[direction]].piece << 12) ^ (
                                  self.board[i + 4 * dx[direction]][j + 4 * dy[direction]].piece << 14)
                    self.board[i][j].pattern[direction][0] = patternTable[key][0]
                    self.board[i][j].pattern[direction][1] = patternTable[key][1]
                    self.board[i][j].update_value()

    def isFree(self, x, y):
        return x >= 4 and y >= 4 and x < self.width + 4 and y < self.height + 4

    def setplayer(self, player):
        self.who = player
        self.opp = player ^ 1


    def move(self, x, y):
        self.board[x][y].piece = self.who
        self.step += 1
        self.who ^= 1
        self.opp ^= 1
        self.record.append(self.board[x][y])
        self.updatePattern(x, y)
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if i == x and j == y:
                    continue
                if self.isFree(i, j):
                    self.board[i][j].iscand += 1

    def delmove(self):
        reset = self.record.pop()
        x, y = reset.x, reset.y
        self.step -= 1
        self.who ^= 1
        self.opp ^= 1
        self.board[x][y].piece = Empty
        self.updatePattern(x, y)

        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if i == x and j == y:
                    continue
                if self.isFree(i, j):
                    self.board[i][j].iscand -= 1

    def updatePattern(self, x, y):  # Update patterns of pieces around the target
        for direction in range(0,4):
            x_0 = x - 4*dx[direction]
            y_0 = y - 4*dy[direction]
            for j in range(0,9):
                if j == 4:
                    continue
                x_1 = x_0 + j*dx[direction]
                y_1 = y_0 + j*dy[direction]
                if not self.isFree(x_1,y_1):
                    continue
                key = (self.board[x_1 - 4 * dx[direction]][y_1 - 4 * dy[direction]].piece) ^ (
                        self.board[x_1 - 3 * dx[direction]][y_1 - 3 * dy[direction]].piece << 2) \
                      ^ (self.board[x_1 - 2 * dx[direction]][y_1 - 2 * dy[direction]].piece << 4) ^ (
                              self.board[x_1 - dx[direction]][y_1 - dy[direction]].piece << 6) \
                      ^ (self.board[x_1 + dx[direction]][y_1 + dy[direction]].piece << 8) ^ (
                              self.board[x_1 + 2 * dx[direction]][y_1 + 2 * dy[direction]].piece << 10) \
                      ^ (self.board[x_1 + 3 * dx[direction]][y_1 + 3 * dy[direction]].piece << 12) ^ (
                              self.board[x_1 + 4 * dx[direction]][y_1 + 4 * dy[direction]].piece << 14)
                self.board[x_1][y_1].pattern[direction][0] = patternTable[key][0]
                self.board[x_1][y_1].pattern[direction][1] = patternTable[key][1]
                self.board[x_1][y_1].update_value()


    def isType(self,x,y,Type,role):
        for direction in range(0,4):
            if self.board[x][y].pattern[direction][role] == Type:
                return True
        return False

    def getwinner(self):
        for i in range(4,Width+4):
            for j in range(4,Height+4):
                if self.board[i][j].piece != Empty:
                    if self.isType(i,j,win,self.board[i][j].piece):
                        return self.board[i][j].piece
        return 2  # no winner

    def isfull(self):
        for i in range(4,Width+4):
            for j in range(4,Height+4):
                if self.board[i][j].piece == Empty:
                    return False
        return True

    def getmoves(self):   # 选择周围一格内有邻居的空节点。movevalue sort 这里没用到
        moves = []
        for i in range(4,Width+4):
            for j in range(4,Height+4):
                if self.board[i][j].piece == Empty and self.board[i][j].iscand > 0:
                    moves.append((i,j))
                    score = self.moveEstimate(i,j)
                    self.board[i][j].movevalue = score
        moves.sort(key=lambda m: -self.board[m[0]][m[1]].movevalue)
        return moves




    def simulation(self):
        if self.timecontrol >= 16:
            return 0.5
        self.timecontrol += 1
        who = self.getwinner()
        if who == 0:
            return 1
        if who == 1:
            return 0
        if who == 2 and self.isfull():
            return 0.5
        moves = self.getmoves()

        for move in moves:   # if win or lose, simulate
            if self.isType(move[0],move[1],win,0):
                self.move(move[0],move[1])
                v = self.simulation()
                self.delmove()
                return v
        for move in moves:
            if self.isType(move[0],move[1],win,1):
                self.move(move[0],move[1])
                v = self.simulation()
                self.delmove()
                return v
        for move in moves:
            if self.isType(move[0],move[1],flex4,0):
                self.move(move[0],move[1])
                v = self.simulation()
                self.delmove()
                return v
        for move in moves:
            if self.isType(move[0],move[1],flex4,1):
                self.move(move[0],move[1])
                v = self.simulation()
                self.delmove()
                return v

        for move in moves:   # live 3 , simulate randomly in probability
            if self.isType(move[0],move[1],flex3,1):
                i = random.random()
                if i >0.8:
                    continue
                else:
                    self.move(move[0],move[1])
                    v = self.simulation()
                    self.delmove()
                    return v

        for move in moves:   # live 3 , simulate randomly in probability
            if self.isType(move[0],move[1],flex3,0):
                i = random.random()
                if i >0.7:
                    continue
                else:
                    self.move(move[0],move[1])
                    v = self.simulation()
                    self.delmove()
                    return v

        x,y = random.choice(moves)   # No specific patterns, random simulation
        self.move(x,y)
        v = self.simulation()
        self.delmove()
        return v
        # x,y = random.choice(moves)
        # self.move(x,y)
        # v = self.simulation()
        # self.delmove()
        # return v

    def getbestmove(self):
        moves = self.getmoves()

        for move in moves:
            if self.isType(move[0],move[1],win,0):   # if win or lose, return directly
                return move
        for move in moves:
            if self.isType(move[0],move[1],win,1):
                return move
        for move in moves:
            if self.isType(move[0],move[1],flex4,0):
                return move
        for move in moves:
            if self.isType(move[0],move[1],flex4,1):
                return move

        moves = moves[:8]

        for move in moves:   # simulate "times" times for each successor
            x,y = move
            self.move(x,y)
            for _ in range(times):
                r = self.simulation()
                self.timecontrol = 0
                self.count_dict[move] += r
            self.delmove()
        bestmove = max(moves, key=lambda x:self.count_dict[x]) if moves else None
        for move in moves:
            self.count_dict[move] = 0
        return bestmove



    def moveEstimate(self, x, y):
        score = [0, 0]
        score[self.who] = self.board[x][y].value[self.who]
        score[self.opp] = self.board[x][y].value[self.opp]
        if score[self.who] >= 200 or score[self.opp] >= 200:
            if score[self.who] >= score[self.opp]:
                return 2 * score[self.who]
            else:
                return score[self.opp]
        return score[self.who] * 2 + score[self.opp]


    def Search(self):
        if self.step == 0:
            return self.width // 2, self.height // 2
        best = self.getbestmove()
        #_, best = self.max_value(0,float("-inf"),float("inf"))
        return best[0] - 4, best[1] - 4