import copy
from FiveInRowPlayers import FiveInRowPlayer

class MinimaxPlayer(FiveInRowPlayer):

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
        diagonalParamList = [(0, 0, 1, 1), (size, size, -1, 1)]

        for p in range(1, size+1):
            diagonalParamList += [(0, p, 1, 1), (p, 0, 1, 1)] #north-east diagonals
            diagonalParamList += [(size, p, -1, 1), (size-p, 0, -1, 1)] #nort-west diagonals

        for diagonalParams in diagonalParamList:
            diag = self.getOneDiagonal(board, *diagonalParams)
            if len(diag) >= 5:
                diags.append(diag)

        return diags

    def evaluateLine(self, line, myTurn):

        lineLen = len(line)
        if lineLen < 5:
            return 0

        idx=0
        while line[idx] == '.':
            idx +=1
            if idx >= lineLen:
                return 0

        scoreTable = [0, 1, 2, 50, 200, 1000, 1000, 1000]

        startIdx = idx
        markToSearch = line[idx]
        marksFound = 1
        patternLen = 0
        scoreFactor = 1

        if myTurn and markToSearch == self.opponentMark:
            scoreFactor = -1

        for c in line[idx:]:
            if c == markToSearch:
                marksFound += 1
            elif c == '.':
                pass
            else: #opponent mark
                break

            patternLen+=1
            if patternLen > 6:
                break

        if patternLen < 5:
            scoreFactor *= 0

        elif patternLen >= 5 and startIdx > 0:
            scoreFactor *= 10

        if startIdx > 0: startIdx -= 1
        nextIdx = startIdx + patternLen
        score = scoreTable[marksFound] * scoreFactor
        score += self.evaluateLine(line[nextIdx:], myTurn)

        return score


    def evaluateBoard(self, board, myTurn):
        lines = []
        lines += self.getRows(board)
        lines += self.getCols(board)
        lines += self.getDiagonals(board)

        score = 0
        for line in lines:
            score += self.evaluateLine(line, myTurn)
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
            return self.evaluateBoard(board, maximizing), (-1,-1)

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
