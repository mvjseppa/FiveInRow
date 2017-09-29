import copy
from FiveInRowPlayers import FiveInRowPlayer

class MinimaxPlayer(FiveInRowPlayer):

    def __init__(self):
        super().__init__()
        self.gameStatus = None

    def setGame(self, game):
        super().setGame(game)
        self.gameStatus = MinimaxStatus(game.board, 0)

    def minimax(self, gameStatus, depth, maximizing):

        if gameStatus.gameOver or depth == 0:
            return gameStatus.score, (-1,-1)

        moves = gameStatus.getPossibleMoves()
        bestMove = None

        if maximizing:
            bestScore = -200000
        else:
            bestScore = 200000

        for move in moves:
            clone = copy.deepcopy(gameStatus)

            if maximizing: clone.update(*move, self.number)
            else: clone.update(*move, self.opponentNumber)

            score = self.minimax(clone, depth-1, not maximizing)[0]
            if maximizing and score > bestScore:
                bestScore = score
                bestMove = move
            elif not maximizing and score < bestScore:
                bestScore = score
                bestMove = move

        print(depth, len(moves), bestScore)
        return bestScore, bestMove

    def requestMove(self):
        self.gameStatus.update(*(self.game.lastMove), self.opponentNumber)
        move = self.minimax(self.gameStatus, 5, self.number==1)[1]

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
    def __init__(self, board, score):
        self.size = len(board)
        self.board = copy.deepcopy(board)
        #self.possibleMoves = self.possibleMoves() #copy.copy(possibleMoves)
        self.score = score
        self.gameOver = False

    def onBoard(self, x,y):
        return 0 <= x < self.size and 0 <= y < self.size

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

        ds1, ds2 = self.diagonalStartingPoints(x,y)

        linesOld = [
            ''.join([str(item) for item in self.board[y]]),
            ''.join([str(item) for item in [row[x] for row in self.board]]),
            self.getDiagonal(*ds1, 1, 1),
            self.getDiagonal(*ds2, -1, 1)
        ]

        scoreOld = sum( [self.evaluateLine(line) for line in linesOld] )

        self.board[y][x] = int(player)

        linesNew = [
            ''.join([str(item) for item in self.board[y]]),
            ''.join([str(item) for item in [row[x] for row in self.board]]),
            self.getDiagonal(*ds1, 1, 1),
            self.getDiagonal(*ds2, -1, 1)
        ]

        scoreNew = sum( [self.evaluateLine(line) for line in linesNew] )
        self.score += scoreNew - scoreOld

        #try:
        #    self.possibleMoves.remove((x,y))
        #except KeyError:
        #    pass

        #self.possibleMoves.update(self.moveNeighbours(x,y))
        #self.possibleMoves = self.getPossibleMoves()

        #if not self.possibleMoves:
        #    self.gameOver = True

    def evaluateLine(self, line):
        scoreP1 = 0
        scoreP2 = 0

        if line.count("22222") > 0:
            scoreP2 = 10000
            self.gameOver = True
        elif line.count("11111") > 0:
            scoreP1 = 10000
            self.gameOver = True
        else:
            scoreP1 += line.count('011110') * 10
            scoreP1 += line.count('01110')

            scoreP2 += line.count('022220') * 10
            scoreP2 += line.count('02220')

        score = scoreP1 - scoreP2

        return score


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
        moves = set()

        for x in range(self.size):
            for y in range(self.size):
                if self.isPossibleMove(x, y):
                    moves.add((x,y))
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
