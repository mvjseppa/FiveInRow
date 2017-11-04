import copy
from collections import deque
from FiveInRowPlayers import FiveInRowPlayer

class MinimaxPlayer(FiveInRowPlayer):

    def __init__(self, depth):
        super().__init__()
        self.gameStatus = None
        self.searchDepth = depth
        self.transpTable = dict()
        self.transpTablePrev = dict()
        self.nodeNo = 0

    def setGame(self, game):
        super().setGame(game)
        self.gameStatus = MinimaxStatus(game.board, game.turn)

    def minimax(self, gameStatus, depth, alpha, beta, maximizing):

        if gameStatus.gameOver or depth == 0:
            score = gameStatus.getScore(maximizing)
            return score, (-1,-1)

        statusKey = gameStatus.key()
        try:
            #if this position is already searched, return result from transposition
            result = self.transpTable[statusKey]
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
        if self.game.lastMove is not None:
            self.gameStatus.update(*(self.game.lastMove), self.opponentNumber)

        self.nodeNo = 0

        self.transpTablePrev = self.transpTable
        self.transpTable = dict()
        score, move = self.minimax(self.gameStatus, self.searchDepth, -200000, 200000, self.number==1)

        print("minimax result:", score, move)

        if not self.gameStatus.onBoard(*move):
            print("Minimax move not on board!")
            exit(-1)

        if self.gameStatus.board[move[1]][move[0]] != 0:
            print("Minimax tries to play on non-free spot!")
            exit(-1)

        self.gameStatus.update(*move, self.number)
        #print("minimax board: \n",str(self.gameStatus), "\n\n")

        return move

class MinimaxStatus:
    def __init__(self, board, turnNo):
        self.size = len(board)
        self.board = copy.deepcopy(board)
        self.gameOver = False
        self.turnNo = turnNo

    def key(self):
        return str(self.board)

    def onBoard(self, x,y):
        return 0 <= x < self.size and 0 <= y < self.size

    def getScore(self, maximizing):

        lines = []
        ev = dict()
        ev["P1"] = self.PlayerScore()
        ev["P2"] = self.PlayerScore()

        for x in range(self.size):
            lines.append(self.getDiagonal(x, 0, 1, 1))
            lines.append(self.getDiagonal(x, 0, -1, 1))

        for x in range(self.size-1):
            lines.append(self.getDiagonal(0, x+1, 1, 1))
            lines.append(self.getDiagonal(self.size-1, x+1, -1, 1))

        for row in self.board:
            lines.append(''.join([str(item) for item in row]))

        for row in zip(*(self.board)):
            lines.append(''.join([str(item) for item in row]))

        for line in lines: self.evaluateLine(line, ev)

        score = 0

        lastPlr, nextPlr = "P2", "P1"
        if not maximizing:
            lastPlr, nextPlr = nextPlr, lastPlr

        if ev[nextPlr].fives > 0:
            score = -1000

        elif ev[lastPlr].fives > 0:
            score = 1000

        elif ev[nextPlr].openFours > 0 or ev[nextPlr].fours > 0:
            score = -100

        elif ev[lastPlr].openFours > 0:
            score = 100

        elif ev[nextPlr].openThrees > 0 and ev[lastPlr].fours == 0:
            score = -50

        elif ev[lastPlr].openThrees + ev[lastPlr].fours > 1:
            score = 50

        else:
            score = 10 * ev[lastPlr].openThrees + ev[lastPlr].openTwos

        if maximizing: return -1 * score
        return score


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
        self.turnNo += 1

    def evaluateLine(self, line, ev):

        ev["P1"].fives += line.count("11111")
        ev["P2"].fives += line.count("22222")

        if ev["P1"].fives or ev["P2"].fives:
            self.gameOver = True
            return

        ev["P1"].openFours += line.count("011110")
        ev["P2"].openFours += line.count("022220")

        ev["P1"].fours += line.count("211110")
        ev["P1"].fours += line.count("011112")
        ev["P2"].fours += line.count("122220")
        ev["P2"].fours += line.count("022221")

        ev["P1"].openThrees += line.count("01110")
        ev["P2"].openThrees += line.count("02220")

        ev["P1"].openTwos += line.count("001100")
        ev["P2"].openTwos += line.count("002200")

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

        if self.turnNo == 0:
            mid = int(self.size/2)
            moves.append((mid,mid))
        else:
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

    class PlayerScore:
        openFours = 0
        fives = 0
        fours = 0
        openThrees = 0
        openTwos = 0
