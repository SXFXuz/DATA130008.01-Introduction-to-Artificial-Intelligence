import random
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG
from Estimator import patternTable
from Estimator import pvalTable as valueTable
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
        for i in range(x - 2, x + 3):
            for j in range(y - 2, y + 3):
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

        for i in range(x - 2, x + 3):
            for j in range(y - 2, y + 3):
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


    def boardEstimate(self):
        score = {self.who: 0, self.opp: 0}
        for item in self.record:
            score[item.piece] += item.value[item.piece]
        return score[self.who] - score[self.opp]


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


    def getCandidates(self):
        cand_list = []
        n = 0
        for i in range(4, self.width + 4):
            for j in range(4, self.width + 4):
                if self.board[i][j].piece == Empty and self.board[i][j].iscand > 0:
                    score = self.moveEstimate(i, j)
                    self.board[i][j].movevalue = score
                    if score > 0:
                        cand_list.append(self.board[i][j])
                        n += 1
        cand_list.sort(key=lambda cand: -cand.movevalue)
        if cand_list[0].movevalue >= 2400:  # live4 or higher priority
            return [cand_list[0]], 1
        if cand_list[0].movevalue == 1200:  # live3 opp
            cand_newlist = []
            n_new = 0
            for i in range(0, n):  # search for live4
                if cand_list[i].movevalue == 1200:
                    cand_newlist.append(cand_list[i])
                    n_new += 1
                else:
                    break
            for i in range(n_new, n):  # search for sleep4
                p = False
                for direction in range(4):
                    if cand_list[i].pattern[direction][0] == block4 or cand_list[i].pattern[direction][1] == block4:
                        p = True
                        break
                if p:
                    cand_newlist.append(cand_list[i])
                    n_new += 1
            if n_new != 0:
                return cand_newlist, n_new
        return cand_list, n

    def minimax(self, depth, alpha, beta):
        if depth == MaxDepth:
            return self.boardEstimate(), [4, 4]
        cand_list, n = self.getCandidates()
        if n == 0:
            return 0, [4, 4]
        cand_list = cand_list[0:min(n, branchFactor)]
        v = float("-inf")
        max_v = 0
        max_position = [4, 4]
        for cand in cand_list:
            self.move(cand.x, cand.y)
            value, _ = self.minimax(depth + 1, -beta, -alpha)
            self.delmove()
            if -value > v:
                max_position[0] = cand.x
                max_position[1] = cand.y
                v = -value
                max_v = v
            alpha = max(alpha, v)
            if v >= beta:
                return max_v, max_position
        return max_v, max_position

    # def max_value(self,depth,alpha,beta):
    #     if depth == MaxDepth:
    #         return self.boardEstimate(), [4,4]
    #     cand_list, n = self.getCandidates()
    #     if n == 0:
    #         return 0, [4,4]
    #     cand_list = cand_list[0:min(n, branchFactor)]
    #     v_max = float("-inf")
    #     v = float("-inf")
    #     position = [4,4]
    #     for cand in cand_list:
    #         self.move(cand.x, cand.y)
    #         value,_ = self.min_value(depth+1, alpha, beta)
    #         self.delmove()
    #         if value > v:
    #             v_max = value
    #             position[0] = cand.x
    #             position[1] = cand.y
    #             v = value
    #         alpha = max(alpha, v)
    #         if v >= beta:
    #             return v_max, position
    #     return v_max, position
    #
    # def min_value(self,depth,alpha,beta):
    #     if depth == MaxDepth:
    #         return self.boardEstimate(), [4,4]
    #     cand_list, n = self.getCandidates()
    #     cand_list = cand_list[0:min(n, branchFactor)]
    #     if n == 0:
    #         return 0, [4,4]
    #     v_min = float("inf")
    #     v = float("inf")
    #     position = [4,4]
    #     for cand in cand_list:
    #         self.move(cand.x, cand.y)
    #         value,_ = self.max_value(depth+1, alpha, beta)
    #         self.delmove()
    #         if value < v:
    #             v_min = value
    #             position[0] = cand.x
    #             position[1] = cand.y
    #             v = value
    #         beta = min(beta, v)
    #         if v <= alpha:
    #             return v_min, position
    #     return v_min, position


    def Search(self):
        if self.step == 0:
            return self.width // 2, self.height // 2
        _, best = self.minimax(0, float("-inf"), float("inf"))
        #_, best = self.max_value(0,float("-inf"),float("inf"))
        return best[0] - 4, best[1] - 4

