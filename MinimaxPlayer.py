import copy
from collections import OrderedDict, deque
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
            print(self.gameStatus.possibleMoves)

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
        self.board = [x[:] for x in [[0] * self.size] * self.size]
        self.gameOver = False
        self.turnNo = turnNo
        self.lastMove = None

        mid = int(self.size/2)
        self.possibleMoves = [(mid,mid)]

        for x in range(self.size):
            for y in range(self.size):
                if board[y][x] != 0:
                    self.update(x,y,int(board[y][x]))

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
            score = -900

        elif ev[lastPlr].openFours > 0:
            score = 800

        elif ev[nextPlr].openThrees > 0 and ev[lastPlr].fours == 0:
            score = -100 * ev[nextPlr].openThrees

        elif ev[lastPlr].openThrees + ev[lastPlr].fours > 1:
            score = 100 * (ev[lastPlr].openThrees + ev[lastPlr].fours)

        else:
            score = 10 * ev[lastPlr].openThrees + ev[lastPlr].openTwos - ev[nextPlr].openTwos

        return -score if maximizing else score

    def getDiagonal(self, x0, y0, dx, dy):
        strdiag = ''
        x, y = x0, y0

        while self.onBoard(x,y):
            strdiag += str(self.board[y][x])
            x, y = x + dx, y + dy

        return strdiag


    def update(self, x0, y0, player):
        self.board[y0][x0] = int(player)

        self.possibleMoves = self.getPriorityMoves(x0,y0) + self.possibleMoves
        self.possibleMoves = list(OrderedDict.fromkeys(self.possibleMoves))

        neighbours = lambda p: [p-1, p, p+1]
        for x in neighbours(x0):
            for y in neighbours(y0):
                if not self.onBoard(x,y):
                    continue
                elif self.board[y][x] == 0 and self.possibleMoves.count((x,y)) == 0:
                    self.possibleMoves.appendleft((x,y))

        try:
            self.possibleMoves.remove((x0,y0))
        except(ValueError):
            pass
        self.lastMove = (x0,y0)
        self.turnNo += 1


    def getPriorityMoves(self, x0, y0):
        moves = []
        dirs = [
            lambda x,y: (x+1, y),
            lambda x,y: (x-1, y),
            lambda x,y: (x, y+1),
            lambda x,y: (x, y-1),
            lambda x,y: (x+1, y+1),
            lambda x,y: (x-1, y+1),
            lambda x,y: (x+1, y-1),
            lambda x,y: (x-1, y-1)
        ]

        for d in dirs:
            x,y = x0, y0
            while self.onBoard(x,y):
                if self.board[y][x] == 0:
                    moves.append((x,y))
                    break
                x,y = d(x,y)

        return moves



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

    def getPossibleMoves(self):
        return deque(self.possibleMoves)

    def __str__(self):
        marks = ['.', 'X', 'O']
        return '\n'.join([''.join([marks[item] for item in row]) for row in self.board])

    class PlayerScore:
        openFours = 0
        fives = 0
        fours = 0
        openThrees = 0
        openTwos = 0
