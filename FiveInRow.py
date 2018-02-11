from FiveInRowPlayers import *
from MinimaxPlayer import MinimaxPlayer
import threading

class FiveInRow(threading.Thread):

    def __init__(self, player1, player2):
        threading.Thread.__init__(self)

        self.size = 15
        #self.board = [[0] * self.size] * self.size
        self.board = [x[:] for x in [[0] * self.size] * self.size]
        #self.board = []
        #for _ in range(self.size): self.board.append('.'*self.size)

        player1.setNumber(1)
        player2.setNumber(2)
        self.players = (player1, player2)
        self.turn = 0
        for player in self.players: player.setGame(self)
        self.lastMove = None
        self.moves = []

    def getBoardPos(self, x, y):
        return self.board[y][x]

    def setBoardPos(self, x, y , mark):
        self.board[y][x] = mark

    def changeTurn(self):
        self.players = self.players[1], self.players[0]

    def onBoard(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def checkWin(self, board, x0, y0):

        directions = [
            [1, 0], #horizontal
            [0, 1], #vertical
            [1, 1], #diagonal 1
            [1, -1] #diagonal 2
        ]

        mark = board[y0][x0]

        for direction in directions:
            dx, dy = direction
            x, y = x0, y0
            marksInRow = 0

            for _ in range(2):
                while self.onBoard(x, y) and board[y][x] == mark:
                    x += dx
                    y += dy
                    marksInRow += 1

                #check the negative direction also
                dx *= -1
                dy *= -1
                x = x0 + dx
                y = y0 + dy

            if marksInRow >= 5:
                return True

        return False

    def tick(self):
        moveDone = False
        while not moveDone:
            move = self.players[0].requestMove()
            if not self.onBoard(*move):
                continue

            if self.getBoardPos(*move) == 0:
                self.setBoardPos(*move, self.players[0].number)
                self.turn += 1
                self.lastMove = move
                self.moves.append(move)
                moveDone = True

        if self.turn >= self.size**2:
            for player in self.players: player.notifyDraw()
            return False #game over

        if self.checkWin(self.board, *move):
            self.players[0].notifyWin()
            self.players[1].notifyLoss()
            return False #game is over

        self.players[0].notifyMoveOk()
        self.changeTurn()
        return True #game continues

    def run(self):
        while self.tick():
            print(self.turn)
            print(str(self))
        print(str(self))

    def __str__(self):
        marks = ['.', 'X', 'O']
        return '\n'.join([''.join([marks[item] for item in row]) for row in self.board])


def main():
    p1 = HumanPlayer("Mikko")
    #p2 = HumanPlayer("Kaisa")
    #p1 = ShallowAiPlayer()
    p1 = MinimaxPlayer(5)
    p2 = MinimaxPlayer(5)

    game = FiveInRow(p1, p2)

    game.start()
    game.join()

if __name__ == "__main__":
    main()
