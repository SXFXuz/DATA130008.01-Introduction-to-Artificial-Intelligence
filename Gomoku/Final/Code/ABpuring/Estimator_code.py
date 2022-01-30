

Width = 20
Height = 20
MaxDepth = 6
Factor = 6

dx = [1,0,1,1]
dy = [0,1,1,-1]   #方向向量


win = 7  # pattern
flex4 = 6
block4 = 5
flex3 = 4
block3 = 3
flex2 = 2
block2 = 1


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
L= 3
M = 2
N = 1
FORBID = 15



def generate_assist(len, len2, count, block):
    if len >= 5 and count > 1:
        if count == 5:
            return win
        if len > 5 and len2 < 5 and block == 0:
            if count == 2:
                return flex2
            if count == 3:
                return flex3
            if count == 4:
                return flex4
        else:
            if count == 2:
                return block2
            if count == 3:
                return block3
            if count == 4:
                return block4
    return 0

def getPval(a,b,c,d):
    type = [0 for i in range(9)]
    type[a] += 1
    type[b] += 1
    type[c] += 1
    type[d] += 1
    if type[win] > 0:
        return 5000
    if type[flex4] >0 or type[block4] >1:
        return 1200
    if type[block4] >0 and type[flex3] > 0:
        return 1000
    if type[flex3] > 1:
        return 200
    val = [0,2,5,5,12,12]
    score = 0
    for i in range(1,block4+1):
        score += val[i] * type[i]
    return score

def Full_Shape(a,b,c,d):
    n = [0 for i in range(8)]
    n[a] += 1
    n[b] += 1
    n[c] += 1
    n[d] += 1
    if (n[win] >= 1):
        return A # OOOO_
    if (n[flex4] >= 1):
        return B #OOO_
    if (n[block4] >= 2):
        return B # XOOO_ * _OOOX
    if (n[block4] >= 1 and n[flex3] >= 1):
        return C # XOOO_ * _OO
    if (n[block4] >= 1 and n[block3] >= 1) :
        return D # XOOO_ * _OOX
    if (n[block4] >= 1 and n[flex2] >= 1):
        return D # XOOO_ * _O
    if (n[block4] >= 1 and n[block2] >= 1):
        return E # XOOO_ * _OX
    if (n[block4] >= 1):
        return F # XOOO_
    if (n[flex3] >= 2):
        return G # OO_ * _OO
    if (n[flex3] >= 1 and n[block3] >= 1):
        return H  #OO_ * _OOX
    if (n[flex3] >= 1 and n[flex2] >= 1):
        return H # OO_ * _O
    if (n[flex3] >= 1 and n[block2] >= 1):
        return I # OO_ * _OX
    if (n[flex3] >= 1):
        return J # OO_
    if (n[block3] + n[flex2] >= 2):
        return K # O_ * _OOX
    if (n[block3] >= 1):
        return L # _OOX
    if (n[flex2] >= 1):
        return M # _O
    if (n[block2] >= 1):
        return N # _OX
    return 0

def init_fullpattern():
    fullpattern_table = [[[[0 for _ in range(8)] for _ in range(8)] for _ in range(8)] for _ in range(8)]
    for a in range(8):
        for b in range(8):
            for c in range(8):
                for d in range(8):
                    fullpattern_table[a][b][c][d] = Full_Shape(a, b, c, d)
    return fullpattern_table


def init_chess_type():
    # 棋型判断辅助表
    typeTable = [[[[0 for _ in range(3)] for _ in range(6)] for _ in range(6)] for _ in range(10)]
    for i in range(0,10):
        for j in range(0,6):
            for k in range(0,6):
                for l in range(0,3):
                    typeTable[i][j][k][l] = generate_assist(i,j,k,l)
    return typeTable


    # 棋型表
def init_chess_pattern():
    patternTable = [[0 for _ in range(2)] for _ in range(65536)]
    for key in range(0,65536):
        patternTable[key][0] = LineType(0,key)
        patternTable[key][1] = LineType(1,key)
    # 走法评价表
    return patternTable

# 分数表
def init_chess_pval():
    pval = [[[[0 for _ in range(8)] for _ in range(8)] for _ in range(8)] for _ in range(8)]
    for i in range(0,8):
        for j in range(0,8):
            for k in range(0,8):
                for l in range(0,8):
                    pval[i][j][k][l] = getPval(i,j,k,l)
    return pval



# 判断key的棋型，用于填充棋型表
def LineType(role,key):
    line_left = []
    for i in range(9):
        if i == 4:
            line_left.append(role)
        else:
            line_left.append(key & 3)
            key >>= 2
    line_right = list(reversed(line_left))

    p1 = shortLine(line_left)
    p2 = shortLine(line_right)
    # 分别从两个方向识别
    if p1 == block3 and p2 == block3:
        return checkFlex3(line_left)
    if p1 == block4 and p2 == block4:
        return checkFlex4(line_left)
    if p1 > p2:
        return p1
    else:
        return p2

def checkFlex3(line):
    role = line[4]
    for i in range(9):
        if line[i] == Empty:
            line[i] = role
            type = checkFlex4(line)
            line[i] = Empty
            if type == flex4:
                return flex3
    return block3

def checkFlex4(line):
    five = 0
    role = line[4]
    for i in range(9):
        if line[i] == Empty:
            count = 0
            for j in range(i-1, -1, -1):
                if line[j] != role:
                    break
                count += 1
                j -= 1
            for j in range(i+1, 9):
                if line[j] != role:
                    break
                count += 1
                j += 1
            if count >= 4:
                five += 1
    if five >= 2:
        return flex4
    else:
        return block4


def shortLine(line):
    kong = 0
    block = 0
    len = 1
    len2 = 1
    count = 1
    who = line[4]
    for k in range(5,9):
        if line[k] == who:
            if kong+count >4:
                break
            count += 1
            len += 1
            len2 = kong + count
        elif line[k] == Empty:
            len += 1
            kong += 1
        else:
            if line[k-1] == who:
                block += 1
            break
    kong = len2 - count
    for k in range(3,-1,-1):
        if line[k] == who:
            if kong+count >4:
                break
            count += 1
            len += 1
            len2 = kong+count
        elif line[k] == Empty:
            len += 1
            kong += 1
        else:
            if line[k+1] == who:
                block += 1
            break
    return typeTable[len][len2][count][block]


typeTable = init_chess_type()
patternTable = init_chess_pattern()
pvalTable = init_chess_pval()
fullpatternTable = init_fullpattern()
# print(patternTable[0b1010001010111111][0])


