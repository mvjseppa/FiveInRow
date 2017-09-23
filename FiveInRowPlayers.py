import random
import FiveInRow
import copy
from abc import ABC, abstractmethod

class FiveInRowPlayer(ABC):
    def __init__(self):
        self.mark = 'X'
        self.opponentMark = 'O'
        self.game = None
        super().__init__()

    def setGame(self, game):
        self.game = game

    def setMarks(self, mark, opponentMark):
        self.mark = mark
        self.opponentMark = opponentMark

    @abstractmethod
    def requestMove(self):
        pass

    def notifyInvalidMove(self):
        pass

    def notifyWin(self):
        pass

    def notifyLoss(self):
        pass

    def notifyDraw(self):
        pass


class HumanPlayer(FiveInRowPlayer):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def printBoard(self):
        print ("\n\n")
        print ("Turn:", self.game.turn)
        print (self.game)
        print ("\n")

    def requestMove(self):
        self.printBoard()
        print ("Your turn " + self.name + ":")
        values = list(map(int, input().split(',')))
        return (values[0], values[1])

    def notifyInvalidMove(self):
        self.printBoard()
        print("Invalid move!")

    def notifyWin(self):
        self.printBoard()
        print("You win, " + self.name + "!")

    def notifyLoss(self):
        self.printBoard()
        print("You lose, " + self.name + "!")

    def notifyDraw(self):
        self.printBoard()
        print("It's a draw" + self.name + "!")

class RandomPlayer(FiveInRowPlayer):
    def requestMove(self):
        a = random.randint(0, self.game.size - 1)
        b = random.randint(0, self.game.size - 1)
        return a,b

class ShallowAiPlayer(FiveInRowPlayer):
    def evaluateBoard(self):
        """Evaluate all moves on board and return the best one"""
        moves = {}

        for x in range(0, self.game.size):
            for y in range(0, self.game.size):
                if self.game.board[x][y] != '.':
                    continue

                value = self.evaluateMove((x,y))
                moves[(x,y)] = value

        return max(moves, key=moves.get)

    def countMarksInDirection(self, pos, d, mark, tight=False):
        x, y = pos[0], pos[1]
        count = 0

        while True:
            x += d[0]
            y += d[1]

            if not self.game.onBoard((x,y)):
                break

            if self.game.getBoardPos((x,y)) == mark:
                count += 1

            elif tight and count == 0:
                break

            elif self.game.getBoardPos((x,y)) != '.':
                break #these are not the marks you are looking for

        return count

    def evaluateMove(self, move):
        value = 0

        directions = [
            (1,0),
            (0,1),
            (1,1),
            (1,-1),
        ]

        for d in directions:
            dNeg = (d[0]*-1, d[1]*-1)

            #count my marks
            myMarks = (self.countMarksInDirection(move, d, self.mark) +
                    self.countMarksInDirection(move, dNeg, self.mark))

            myMarksTight = max(self.countMarksInDirection(move, d, self.mark, tight=True),
                    self.countMarksInDirection(move, dNeg, self.mark, tight=True))

            #count opponent's marks
            oppMarks = max(self.countMarksInDirection(move, d, self.opponentMark, tight=True),
                    self.countMarksInDirection(move, dNeg, self.opponentMark, tight=True))

            if oppMarks >= 2:
                value += oppMarks*10

            if myMarksTight >= 2:
                value += myMarks*10

            value += myMarks + oppMarks

        return value

    def requestMove(self):
        return self.evaluateBoard()

class MinimaxPlayer(FiveInRowPlayer):

    def __init__(self):
        self.patterns = [
            ("XXXXX", 10000),
            ("XXXX", 700),
            ("X.XXX", 500),
            ("XX.XX", 500),
            ("XXX.X", 500),
            ("XXX", 100),
            ("X.X.X", 100),
            ("XX.X", 100),
            ("X.XX", 100),
            ("X..XX", 70),
            ("XX..X", 70),
            ("XX", 20),
            ("X.X", 10),
            ("X..X", 5),
            ("X...X", 5)
        ]
        super().__init__()

    def isPossibleMove(self, board, x0, y0):
        for x in range(x0-1, x0+2):
            for y in range(y0-1, y0+2):
                if (x, y) == (x0, y0):
                    continue
                if not self.game.onBoard(x,y):
                    continue
                if board[x][y] != '.':
                    return True
        return False

    def getPossibleMoves(self, board):
        moves = []
        size = self.game.size
        for x in range(size):
            for y in range(size):
                if board[x][y] == '.':
                    if self.isPossibleMove(board, x, y) or x == y == size/2:
                        moves.append((x,y))
        return moves

    def getRows(self, board):
        rows = []
        for row in board: rows.append(''.join(row))
        return rows

    def getCols(self, board):
        cols = []
        for col in range(self.game.size):
            strcol = ''
            for row in board:
                strcol += row[col]
            cols.append(strcol)
        return cols

    def getOneDiagonal(self, board, x0, y0, dx, dy):
        strdiag = ''
        x, y = x0, y0
        while self.game.onBoard(x,y):
            strdiag += board[x][y]
            x, y = x + dx, y + dy
        return strdiag

    def getDiagonals(self, board):
        diags = []
        size = self.game.size - 1

        #list of starting points and directions for getOneDiagonal
        #initialize with the two center diagonals
        diagonalParamList = [(0, 0, 1, 1), (size, size, -1, -1)]

        for p in range(1, size+1):
            diagonalParamList += [(0, p, 1, 1), (p, 0, 1, 1)] #north-east diagonals
            diagonalParamList += [(size, p, -1, 1), (size-p, 0, -1, 1)] #nort-west diagonals

        for diagonalParams in diagonalParamList:
            diag = self.getOneDiagonal(board, *diagonalParams)
            if len(diag) >= 5:
                diags.append(diag)

        return diags

    def evaulateLine(self, line):
        return line.count(self.mark) - line.count(self.opponentMark)

    def evaluateBoard(self, board):
        lines = []
        lines += self.getRows(board)
        lines += self.getCols(board)
        lines += self.getDiagonals(board)

        score = 0
        for line in lines:
            score += self.evaulateLine(line)
        return score

    def cloneBoard(self, board, x, y, myTurn):
        clone = copy.deepcopy(board)

        if myTurn:
            clone[x][y] = self.mark
        else:
            clone[x][y] = self.opponentMark

        return clone

    def isGameOver(self, board, lastMove):
        return self.game.checkWin(board, *lastMove)

    def minimax(self, board, lastMove, depth, maximizing):
        if self.isGameOver(board, lastMove) or depth == 0:
            return self.evaluateBoard(board), (-1,-1)

        moves = self.getPossibleMoves(board)
        bestMove = moves[0]

        if maximizing:
            bestScore = float('-inf')
        else:
            bestScore = float('inf')

        print(depth, len(moves))

        for move in moves:
            clone = self.cloneBoard(board, *move, maximizing)
            score = self.minimax(clone, move, depth-1, not maximizing)[0]
            if maximizing and score > bestScore:
                bestScore = score
                bestMove = move
            elif not maximizing and score < bestScore:
                bestScore = score
                bestMove = move
        return bestScore, bestMove

    def requestMove(self):
        move = self.minimax(self.game.board, self.game.lastMove, 3, True)[1]
        if not self.game.onBoard(*move):
            exit(-1)

        print(move)
        return move

if __name__ == "__main__":
    FiveInRow.main()
