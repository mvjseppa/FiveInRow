import random
import FiveInRow
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


if __name__ == "__main__":
    FiveInRow.main()
