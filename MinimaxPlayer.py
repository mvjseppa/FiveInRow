import copy
from collections import deque
from FiveInRowPlayers import FiveInRowPlayer

class MinimaxPlayer(FiveInRowPlayer):

    def __init__(self):
        super().__init__()
        self.gameStatus = None
        self.searchDepth = 3
        self.transpTable = dict()
        self.transpTablePrev = dict()
        self.nodeNo = 0

    def setGame(self, game):
        super().setGame(game)
        self.gameStatus = MinimaxStatus(game.board, 0, 0)

    def minimax(self, gameStatus, depth, alpha, beta, maximizing):
        self.nodeNo += 1
        print(self.nodeNo)

        if gameStatus.gameOver or depth == 0:
            return gameStatus.getScore(maximizing), (-1,-1)

        statusKey = gameStatus.key()
        try:
            #if this position is already searched, return result from transposition
            result = self.transpTable[statusKey]
            print("transp")
            return result
        except KeyError:
            pass

        bestMove = None
        moves = gameStatus.getPossibleMoves()

        try:
            #first check the best move for this position from previous round
            prevBest = self.transpTablePrev[statusKey]
            moves.appendleft(prevBest[1])
        except KeyError:
            pass

        bestScore = -200000
        if not maximizing:
            bestScore = 200000

        for move in moves:
            clone = copy.deepcopy(gameStatus)

            if maximizing: clone.update(*move, 1)
            else: clone.update(*move, 2)

            score = self.minimax(clone, depth-1, alpha, beta, not maximizing)[0]
            if maximizing and score > bestScore:
                bestScore = score
                alpha = max(alpha, bestScore)
                bestMove = move
            elif not maximizing and score < bestScore:
                bestScore = score
                bestMove = move
                beta = min(beta, bestScore)

            if beta <= alpha:
                break

        if maximizing:
            retval = alpha, bestMove
        else:
            retval = beta, bestMove

        self.transpTable[statusKey] = retval
        return retval

        #print(depth, bestScore)
        #return bestScore, bestMove

    def requestMove(self):
        self.gameStatus.update(*(self.game.lastMove), self.opponentNumber)
        self.nodeNo = 0

        self.transpTablePrev = self.transpTable
        self.transpTable = dict()
        move = self.minimax(self.gameStatus, self.searchDepth, -200000, 200000, self.number==1)[1]

        if not self.gameStatus.onBoard(*move):
            print("Minimax move not on board!")
            exit(-1)

        if self.gameStatus.board[move[1]][move[0]] != 0:
            print("Minimax tries to play on non-free spot!")
            exit(-1)

        self.gameStatus.update(*move, self.number)
        print("minimax board: \n",str(self.gameStatus), "\n\n")

        #print(move)
        return move

class MinimaxStatus:
    def __init__(self, board, score, depth):
        self.size = len(board)
        self.board = copy.deepcopy(board)
        #self.possibleMoves = self.possibleMoves() #copy.copy(possibleMoves)
        self.score = score
        self.depth = depth
        self.gameOver = False
        self.bestPatternP1 = 0
        self.bestPatternP2 = 0

    def key(self):
        return str(self.board)

    def onBoard(self, x,y):
        return 0 <= x < self.size and 0 <= y < self.size

    def getScore(self, maximizing):
        if self.bestPatternP1 == 0 and self.bestPatternP2 == 0:
            return 0

        if maximizing: #player 2 has just played
            if self.bestPatternP2 >= 5:
                return -100
            else:
                return (self.bestPatternP1 + 2) - (self.bestPatternP2)
        else: #player 1 has just played
            if self.bestPatternP1 >= 5:
                return 100
            else:
                return self.bestPatternP1 - (self.bestPatternP2 + 2)

    def diagonalStartingPoints(self, x, y):
        x1, y1, x2, y2 = 0, 0, 0, 0

        if x >= y:
            x1, y1 = x-y, 0
        else:
            x1, y1 = 0, y-x

        end = self.size - 1
        x_ = end - x
        if x_ <= y:
            x2, y2 = end, y-x_
        else:
            x2, y2 = x+y, 0

        return ((x1, y1), (x2, y2))

    def getDiagonal(self, x0, y0, dx, dy):
        strdiag = ''
        x, y = x0, y0

        while self.onBoard(x,y):
            strdiag += str(self.board[y][x])
            x, y = x + dx, y + dy

        return strdiag

    def update(self, x, y, player):

        self.board[y][x] = int(player)
        self.depth += 1

        lines = []

        for x in range(self.size):
            lines.append(self.getDiagonal(x, 0, 1, 1))
            lines.append(self.getDiagonal(self.size-1, x, -1, 1))

        for row in self.board:
            lines.append(''.join([str(item) for item in row]))

        for row in zip(*(self.board)):
            lines.append(''.join([str(item) for item in row]))

        print(str(self))

        for line in lines: self.evaluateLine(line)

    def evaluateLine(self, line):

        if line.count("11111"):
            self.bestPatternP1 = 5
            self.gameOver = True
            return

        if line.count("22222"):
            self.bestPatternP2 = 5
            self.gameOver = True
            return

        if line.count('011110') and self.bestPatternP1 < 4:
            self.bestPatternP1 = 4

        if line.count('01110') and self.bestPatternP1 < 3:
            self.bestPatternP1 = 3

        if line.count('022220') and self.bestPatternP1 < 4:
            self.bestPatternP2 = 4

        if line.count('02220') and self.bestPatternP1 < 3:
            self.bestPatternP2 = 3

        return

    def isPossibleMove(self, x0, y0):
        if self.board[y0][x0] != 0:
            return False

        for x in range(x0-1, x0+2):
            for y in range(y0-1, y0+2):
                if (x, y) == (x0, y0):
                    continue
                if not self.onBoard(x,y):
                    continue
                if self.board[y][x] != 0:
                    return True
        return False

    def getPossibleMoves(self):
        moves = deque()

        for x in range(self.size):
            for y in range(self.size):
                if self.isPossibleMove(x, y):
                    moves.append((x,y))
        return moves

    def moveNeighbours(self, x0, y0):
        neighbours = set()
        for x in range(x0-1, x0+2):
            for y in range(y0-1, y0+2):
                if (x, y) == (x0, y0):
                    continue
                if not self.onBoard(x,y):
                    continue
                if self.board[y][x] == 0:
                    neighbours.add((x,y))
        return neighbours

    def __str__(self):
        marks = ['.', 'X', 'O']
        return '\n'.join([''.join([marks[item] for item in row]) for row in self.board])

class FiveInRowPatterns:
    def __init__(self):
        self.fives = 0
        self.fours = 0
        self.openFours = 0
        self.openThrees = 0
