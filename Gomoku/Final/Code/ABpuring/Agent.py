import random
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG
from Estimator import patternTable
from Estimator import pvalTable as valueTable
from Estimator_code import fullpatternTable
import time

MaxDepth = 6
MAX_VCF_DEPTH = 20
MAX_VCT_DEPTH = 16
MAX_VCT_TIME = 1300


Width = 20
Height = 20
branchFactor = 16

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

A = 14
B = 13
C = 12
D = 11
E = 10
F = 9
G = 8
H = 7
I = 6
J = 5
K = 4
L = 3
M = 2
N = 1
FORBID = 15


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
        self.fullpattern = [0, 0]

    def update_value(self):
        self.value[0] = valueTable[self.pattern[0][0]][self.pattern[1][0]][self.pattern[2][0]][self.pattern[3][0]]
        self.value[1] = valueTable[self.pattern[0][1]][self.pattern[1][1]][self.pattern[2][1]][self.pattern[3][1]]

    def upddate_fullpattern(self):
        self.fullpattern[0] = fullpatternTable[self.pattern[0][0]][self.pattern[1][0]][self.pattern[2][0]][self.pattern[3][0]]
        self.fullpattern[1] = fullpatternTable[self.pattern[0][1]][self.pattern[1][1]][self.pattern[2][1]][self.pattern[3][1]]



class Board:
    def __init__(self):  # board
        self.width = Width
        self.height = Height
        self.board = [[Cell(x, y, 0, 2) for y in range(Height + 8)] for x in range(Width + 8)]
        self.record = []  # moves
        self.step = 0  # Chess number
        self.who = White
        self.opp = Black
        self.nShape = [[0 for _ in range(16)] for _ in range(2)]  # 双方下一步能成的棋型
        self.winPoint = [4,4]
        self.solved = False # debug


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
                self.board[i][j].upddate_fullpattern()

    def isFree(self, x, y):
        return x >= 4 and y >= 4 and x < self.width + 4 and y < self.height + 4

    def setplayer(self, player):
        self.who = player
        self.opp = player ^ 1


    def move(self, x, y):
        self.nShape[0][self.board[x][y].fullpattern[0]] -= 1
        self.nShape[1][self.board[x][y].fullpattern[1]] -= 1
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
        self.board[x][y].upddate_fullpattern()
        self.nShape[0][self.board[x][y].fullpattern[0]] += 1
        self.nShape[1][self.board[x][y].fullpattern[1]] += 1
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
                if self.board[x_1][y_1].piece == Empty:
                    self.nShape[0][self.board[x_1][y_1].fullpattern[0]] -= 1
                    self.nShape[1][self.board[x_1][y_1].fullpattern[1]] -= 1

                self.board[x_1][y_1].pattern[direction][0] = patternTable[key][0]
                self.board[x_1][y_1].pattern[direction][1] = patternTable[key][1]
                self.board[x_1][y_1].update_value()
                self.board[x_1][y_1].upddate_fullpattern()

                if self.board[x_1][y_1].piece == Empty:
                    self.nShape[0][self.board[x_1][y_1].fullpattern[0]] += 1
                    self.nShape[1][self.board[x_1][y_1].fullpattern[1]] += 1


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
        nCand = 0
        cands = []

        for i in range(4, self.width + 4):
            for j in range(4, self.width + 4):
                if self.board[i][j].piece == Empty and self.board[i][j].iscand > 0:
                    score = self.moveEstimate(i, j)
                    self.board[i][j].movevalue = score
                    if score > 0:
                        cands.append(self.board[i][j])
                        nCand += 1
        cands.sort(key=lambda cand: -cand.movevalue)

        if self.nShape[self.who][A] > 0:
            nCand = 1
            return [cands[0]], nCand

        if self.nShape[self.opp][A] > 0:
            nCand = 1
            return [cands[0]], nCand

        if self.nShape[self.who][B] > 0:
            nCand = 1
            return [cands[0]], nCand

        if self.nShape[self.opp][B] > 0:  # 找双方能冲四或活四的点
            cands_new = []
            nCand_new = 0
            for cand in cands:
                if (cand.fullpattern[self.who] >= F) or (cand.fullpattern[self.opp] >= F):
                    cands_new.append(cand)
                    nCand_new += 1
            return cands_new, nCand_new

        return cands, nCand

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


    def findPoint(self, piece, type):
        for i in range(4,24):
            for j in range(4,24):
                if self.board[i][j].piece == Empty and self.board[i][j].iscand:
                    if self.board[i][j].fullpattern[piece] == type:
                        return [i, j]
        return -1

    def VcfStart(self):
        if self.step < 2:
            return -1
        i = self.step - 2
        while i >= 0:
            for j in range(4):
                if self.record[i].pattern[j][self.who] >= block3:
                    return [self.record[i].x, self.record[i].y]
            i -= 2
        return -1


    def VcfSearch1(self):
        startpoint = self.VcfStart()
        if startpoint != -1:
            result = self.VcfSearch2(self.who, 0, startpoint)
            return result
        return 0

    def VcfSearch2(self, searcher, depth, startpoint):
        self.winPoint = [4, 4]
        if self.nShape[self.who][A] >= 1:
            self.winPoint = self.findPoint(self.who, A)
            return 1
        if self.nShape[self.opp][A] >= 2:
            return -2
        if self.nShape[self.opp][A] == 1: # 挡住对方成五点
            oppPoint = self.findPoint(self.opp,A)
            self.move(oppPoint[0], oppPoint[1])
            q = -self.VcfSearch3(searcher, depth+1, startpoint)
            self.delmove()
            if q < 0:
                q -= 1
            elif q > 0:
                self.winPoint = oppPoint
                q += 1
            return q

        if self.nShape[self.who][B] >= 1: # 本方活四，三步胜利
            self.winPoint = self.findPoint(self.who, B)
            return 3

        if self.who == searcher and self.nShape[self.who][C] >= 1: #本方有冲四活三，尝试
            if self.nShape[self.opp][B] == 0 and self.nShape[self.opp][C] == 0 and self.nShape[self.opp][D] == 0 and self.nShape[self.opp][E] == 0 and self.nShape[self.opp][F] == 0:
                self.winPoint = self.findPoint(self.who, C) # 对方没有能成四的点，五步必胜
                return 5
            for i in range(4,24):
                for j in range(4,24):
                    if self.board[i][j].piece == Empty and self.board[i][j].iscand and self.board[i][j].fullpattern[self.who] == C:
                        self.move(i, j)
                        q = -self.VcfSearch3(searcher, depth+1, [i,j])
                        self.delmove()
                        if q > 0:
                            self.winPoint = [i, j]
                            return q+1
        if self.who == searcher and depth < MAX_VCF_DEPTH and (self.nShape[self.who][D] + self.nShape[self.who][E] >= 1): # 本方有冲四或其他棋型
            for direction in range(4):
                for i in range(-4,5):
                    if i == 0:
                        continue
                    x = startpoint[0] + i*dx[direction]
                    y = startpoint[1] + i*dy[direction]
                    if self.board[x][y].piece == Empty and self.board[x][y].iscand:
                        if self.board[x][y].fullpattern[self.who] == D or self.board[x][y].fullpattern[self.who] == E:
                            self.move(x,y)
                            q = -self.VcfSearch3(searcher, depth+1, [x,y])
                            self.delmove()
                            if q > 0:
                                self.winPoint = [x,y]
                                return q+1
        if self.who == searcher and self.nShape[self.who][G] >= 1: # 本方双活三，对方没有任何活四冲四，五步获胜
            if self.nShape[self.opp][B]==0 and self.nShape[self.opp][C]==0 and self.nShape[self.opp][D]==0 and self.nShape[self.opp][E]==0 and self.nShape[self.opp][F]==0:
                self.winPoint = self.findPoint(self.who, G)
                return 5
        return 0



    def VcfSearch3(self, searcher, depth, startpoint):
        if self.nShape[self.who][A] >= 1:
            return 1
        if self.nShape[self.opp][A] >= 2:
            return -2
        if self.nShape[self.opp][A] == 1: #对方下一步成五，挡住成五点
            oppPoint = self.findPoint(self.opp, A)
            self.move(oppPoint[0], oppPoint[1])
            q = -self.VcfSearch3(searcher, depth+1, startpoint)
            self.delmove()
            if q<0:
                q -= 1
            elif q >0:
                q += 1
            return q

        if self.nShape[self.who][B] >= 1: # 本方活四，三步胜利
            return 3
        if self.who == searcher and self.nShape[self.who][C] >= 1: # 本方有冲四活三，尝试
            if self.nShape[self.opp][B] == 0 and self.nShape[self.opp][C] == 0 and self.nShape[self.opp][D] == 0 and self.nShape[self.opp][E] == 0 and self.nShape[self.opp][F] == 0:
                return 5 # 对方没有活四冲四，五步胜利
            for i in range(4,24):
                for j in range(4,24):
                    if self.board[i][j].piece == Empty and self.board[i][j].iscand and self.board[i][j].fullpattern[self.who] == C:
                        self.move(i, j)
                        q = -self.VcfSearch3(searcher, depth+1, [i,j])
                        self.delmove()
                        if q > 0:
                            return q+1

        if self.who == searcher and depth < MAX_VCF_DEPTH and (self.nShape[self.who][D] + self.nShape[self.who][E] >= 1):  # 本方有冲四或其他棋型
            for direction in range(4):
                for i in range(-4, 5):
                    if i == 0:
                        continue
                    x = startpoint[0] + i * dx[direction]
                    y = startpoint[1] + i * dy[direction]
                    if self.board[x][y].piece == Empty and self.board[x][y].iscand:
                        if self.board[x][y].fullpattern[self.who] == D or self.board[x][y].fullpattern[self.who] == E:
                            self.move(x, y)
                            q = -self.VcfSearch3(searcher, depth + 1, [x, y])
                            self.delmove()
                            if q > 0:
                                return q + 1
        if self.who == searcher and self.nShape[self.who][G] >= 1: # 本方双活三，对方没有任何活四冲四，五步获胜
            if self.nShape[self.opp][B]==0 and self.nShape[self.opp][C]==0 and self.nShape[self.opp][D]==0 and self.nShape[self.opp][E]==0 and self.nShape[self.opp][F]==0:
                return 5
        return 0

    def VctStart(self):
        if self.step < 2:
            return -1
        i = self.step -2
        while i>=0:
            for j in range(4):
                if self.record[i].pattern[j][self.who] >= flex2:
                    return [self.record[i].x, self.record[i].y]
            i -= 2
        return -1

    def VctSearch1(self):
        VCT_starttime = time.time()
        startpoint = self.VctStart()
        if startpoint != -1:
            for depth in range(10, MAX_VCT_DEPTH + 2, 2):
                result = self.VctSearch2(self.who, 0, depth, startpoint)
                if result > 0 or (time.time() - VCT_starttime)*4000 >= MAX_VCT_TIME:
                    break
            return result
        return 0

    def VctSearch2(self, searcher, depth, maxdepth, startpoint):
        self.winPoint = [4, 4]
        if self.nShape[self.who][A] >= 1:
            self.winPoint = self.findPoint(self.who, A)
            return 1
        if self.nShape[self.opp][A] >= 2:
            return -2
        if self.nShape[self.opp][A] == 1:  # 挡住对方成五点
            oppPoint = self.findPoint(self.opp, A)
            self.move(oppPoint[0], oppPoint[1])
            q = -self.VctSearch3(searcher, depth + 1, maxdepth, startpoint)
            self.delmove()
            if q < 0:
                q -= 1
            elif q > 0:
                self.winPoint = oppPoint
                q += 1
            return q

        if self.nShape[self.who][B] >= 1:
            self.winPoint = self.findPoint(self.who, B)
            return 3

        if depth > maxdepth:
            return 0

        if self.who != searcher and self.nShape[self.opp][B] >= 1: # 对方算杀方且能活四，防守
            max_q = -1000
            cands, nCand = self.getCandidates()
            for cand in cands:
                self.move(cand.x, cand.y)
                q = -self.VctSearch3(searcher, depth+1, maxdepth, startpoint)
                self.delmove()
                if q>0:
                    self.winPoint = [cand.x, cand.y]
                    return q+1
                elif q == 0:
                    return 0
                elif q > max_q:
                    max_q = q
            return max_q

        if self.who == searcher and self.nShape[self.who][C] >= 1: # 本方算杀方，且有冲四活三，尝试
            if self.nShape[self.opp][B] == 0 and self.nShape[self.opp][C] == 0 and self.nShape[self.opp][D] == 0 and self.nShape[self.opp][E] == 0 and self.nShape[self.opp][F] == 0:
                self.winPoint = self.findPoint(self.who,C)
                # 对方没有冲四以上，五步胜利
                return 5
            for i in range(4,24):
                for j in range(4,24):
                    if self.board[i][j].piece == Empty and self.board[i][j].iscand and self.board[i][j].fullpattern[self.who] == C:
                        self.move(i,j)
                        q = -self.VctSearch3(searcher, depth+1, maxdepth, [i,j])
                        self.delmove()
                        if q > 0:
                            self.winPoint = [i,j]
                            return q + 1

        if self.who == searcher and (self.nShape[self.who][D] + self.nShape[self.who][E] >= 1): # 本方算杀方，尝试所有冲四的点 除冲四活三
            for direction in range(4):
                for i in range(-4,5):
                    if i == 0:
                        continue
                    x = startpoint[0] + i*dx[direction]
                    y = startpoint[1] + i*dy[direction]
                    if self.board[x][y].piece == Empty and self.board[x][y].iscand:
                        if self.board[x][y].fullpattern[self.who] == D or self.board[x][y].fullpattern[self.who] == E:
                            self.move(x,y)
                            q = -self.VctSearch3(searcher, depth+1, maxdepth, [x,y])
                            self.delmove()
                            if q > 0:
                                self.winPoint = [x,y]
                                return q+1

        if self.who == searcher and self.nShape[self.who][G] > 0: # 攻击方尝试双活三
            if self.nShape[self.opp][B] == 0 and self.nShape[self.opp][C] == 0 and self.nShape[self.opp][D] == 0 and self.nShape[self.opp][E] == 0 and self.nShape[self.opp][F] == 0:
                self.winPoint = self.findPoint(self.who, G)
                return 5
            for i in range(4,24):
                for j in range(4,24):
                    if self.board[i][j].piece == Empty and self.board[i][j].iscand and self.board[i][j].fullpattern[self.who] == G:
                        self.move(i, j)
                        q = -self.VctSearch3(searcher, depth+1, maxdepth, [i,j])
                        self.delmove()
                        if q > 0:
                            self.winPoint = [i, j]
                            return q+1

        if self.who == searcher and (self.nShape[self.who][H] + self.nShape[self.who][I] >= 1): # 尝试活三加其他棋型
            for direction in range(4):
                for i in range(-3,4):
                    if i == 0:
                        continue
                    x = startpoint[0] + i*dx[direction]
                    y = startpoint[1] + i*dy[direction]
                    if self.board[x][y].piece == Empty and self.board[x][y].iscand:
                        if self.board[x][y].fullpattern[self.who] == H or self.board[x][y].fullpattern[self.who] == I:
                            self.move(x,y)
                            q = -self.VctSearch3(searcher, depth+1, maxdepth, [x,y])
                            self.delmove()
                            if q > 0:
                                self.winPoint = [x,y]
                                return q+1
        return 0


    def VctSearch3(self, searcher, depth, maxdepth, startpoint):
        if self.nShape[self.who][A] >= 1:
            self.winPoint = self.findPoint(self.who, A)
            return 1
        if self.nShape[self.opp][A] >= 2:
            return -2
        if self.nShape[self.opp][A] == 1:  # 挡住对方成五点
            oppPoint = self.findPoint(self.opp, A)
            self.move(oppPoint[0], oppPoint[1])
            q = -self.VctSearch3(searcher, depth + 1, maxdepth, startpoint)
            self.delmove()
            if q < 0:
                q -= 1
            elif q > 0:
                q += 1
            return q

        if self.nShape[self.who][B] >= 1:
            return 3

        if depth > maxdepth:
            return 0

        if self.who != searcher and self.nShape[self.opp][B] >= 1:  # 对方算杀方且能活四，防守
            max_q = -1000
            cands, nCand = self.getCandidates()
            for cand in cands:
                self.move(cand.x, cand.y)
                q = -self.VctSearch3(searcher, depth + 1, maxdepth, startpoint)
                self.delmove()
                if q > 0:
                    return q + 1
                elif q == 0:
                    return 0
                elif q > max_q:
                    max_q = q
            return max_q

        if self.who == searcher and self.nShape[self.who][C] >= 1:  # 本方算杀方，且有冲四活三，尝试
            if self.nShape[self.opp][B] == 0 and self.nShape[self.opp][C] == 0 and self.nShape[self.opp][D] == 0 and self.nShape[self.opp][E] == 0 and self.nShape[self.opp][F] == 0:
                # 对方没有冲四以上，五步胜利
                return 5
            for i in range(4, 24):
                for j in range(4, 24):
                    if self.board[i][j].piece == Empty and self.board[i][j].iscand and self.board[i][j].fullpattern[self.who] == C:
                        self.move(i, j)
                        q = -self.VctSearch3(searcher, depth + 1, maxdepth, [i, j])
                        self.delmove()
                        if q > 0:
                            return q + 1

        if self.who == searcher and (self.nShape[self.who][D] + self.nShape[self.who][E] >= 1):  # 本方算杀方，尝试所有冲四的点 除冲四活三
            for direction in range(4):
                for i in range(-4, 5):
                    if i == 0:
                        continue
                    x = startpoint[0] + i * dx[direction]
                    y = startpoint[1] + i * dy[direction]
                    if self.board[x][y].piece == Empty and self.board[x][y].iscand:
                        if self.board[x][y].fullpattern[self.who] == D or self.board[x][y].fullpattern[self.who] == E:
                            self.move(x, y)
                            q = -self.VctSearch3(searcher, depth + 1, maxdepth, [x, y])
                            self.delmove()
                            if q > 0:
                                return q + 1

        if self.who == searcher and self.nShape[self.who][G] > 0:  # 攻击方尝试双活三
            if self.nShape[self.opp][B] == 0 and self.nShape[self.opp][C] == 0 and self.nShape[self.opp][D] == 0 and self.nShape[self.opp][E] == 0 and self.nShape[self.opp][F] == 0:
                return 5
            for i in range(4, 24):
                for j in range(4, 24):
                    if self.board[i][j].piece == Empty and self.board[i][j].iscand and self.board[i][j].fullpattern[self.who] == G:
                        self.move(i, j)
                        q = -self.VctSearch3(searcher, depth + 1, maxdepth, [i, j])
                        self.delmove()
                        if q > 0:
                            return q + 1

        if self.who == searcher and (self.nShape[self.who][H] + self.nShape[self.who][I] >= 1):  # 尝试活三加其他棋型
            for direction in range(4):
                for i in range(-3, 4):
                    if i == 0:
                        continue
                    x = startpoint[0] + i * dx[direction]
                    y = startpoint[1] + i * dy[direction]
                    if self.board[x][y].piece == Empty and self.board[x][y].iscand:
                        if self.board[x][y].fullpattern[self.who] == H or self.board[x][y].fullpattern[self.who] == I:
                            self.move(x, y)
                            q = -self.VctSearch3(searcher, depth + 1, maxdepth, [x, y])
                            self.delmove()
                            if q > 0:
                                return q + 1
        return 0


    def rootSearch(self, depth, alpha, beta):
        cand_list, n = self.getCandidates()
        if n == 0:
            return 0, [4, 4]
        cand_list = cand_list[0:min(n, branchFactor)]

        bestpoint = [cand_list[0].x, cand_list[0].y]  # 对方vct
        isallLose = True
        maxloseStep = 0
        for cand in cand_list:
            self.move(cand.x, cand.y)
            lastpoint = self.VcfStart()
            if lastpoint != -1:
                result = self.VctSearch3(self.who, 0, 10, lastpoint)
                if result > 0:
                    cand.movevalue = -300000 # lose
                    if isallLose and (result > maxloseStep):
                        maxloseStep = result
                        bestpoint = [cand.x, cand.y]
                else:
                    if isallLose:
                        isallLose = False
                        bestpoint = [cand.x, cand.y]
            self.delmove()

        cand_list = [cand for cand in cand_list if cand.movevalue != -300000]   # 删除对方vct获胜的点
        n = len(cand_list)
        if n == 0:   # 全败，返回步数最长的点
            return 0, bestpoint
        if n == 1:
            return 0, [cand_list[0].x, cand_list[0].y]

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


    def Search(self):
        if self.step == 0:
            return self.width // 2, self.height // 2

        self.solved = False

        if self.VcfSearch1() > 0:
            self.solved = True
            best = self.winPoint
            return best[0] - 4, best[1] - 4
        if self.VctSearch1() > 0:
            self.solved = True
            best = self.winPoint
            return best[0] - 4, best[1] - 4

        # _, best = self.minimax(0,float("-inf"),float("inf"))
        _, best = self.rootSearch(0, float("-inf"), float("inf"))
        return best[0] - 4, best[1] - 4



