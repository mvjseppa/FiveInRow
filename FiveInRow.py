from FiveInRowPlayers import HumanPlayer
from MinimaxPlayer import MinimaxPlayer

class FiveInRow:

    def __init__(self, player1, player2):
        self.size = 15
        self.board = [x[:] for x in [['.'] * self.size] * self.size]
        #self.board = []
        #for _ in range(self.size): self.board.append('.'*self.size)

        player1.setMarks('X', 'O')
        player2.setMarks('O', 'X')
        self.players = (player1, player2)
        for player in self.players: player.setGame(self)
        self.turn = 0
        self.lastMove = (-1, -1)

    def getBoardPos(self, x, y):
        return self.board[x][y]

    def setBoardPos(self, x, y , mark):
        self.board[x][y] = mark

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

        mark = board[x0][y0]

        for direction in directions:
            dx, dy = direction
            x, y = x0, y0
            marksInRow = 0

            for _ in range(2):
                while self.onBoard(x, y) and board[x][y] == mark:
                    x += dx
                    y += dy
                    marksInRow += 1

                #check the negative direction also
                dx *= -1
                dy *= -1
                x = x0 + dx
                y = y0 + dy

            if self.players[0].mark == 'X':
                print(direction, marksInRow)

            if marksInRow >= 5:
                return True

        return False

    def tick(self):
        moveDone = False
        while not moveDone:
            move = self.players[0].requestMove()
            if not self.onBoard(*move):
                continue

            if self.getBoardPos(*move) == '.':
                self.setBoardPos(*move, self.players[0].mark)
                self.turn += 1
                self.lastMove = move
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

    def __str__(self):
        s = ""
        for row in self.board:
            s += "".join(row) + '\n'
        return s


def main():
    p1 = HumanPlayer("Mikko")
    p2 = MinimaxPlayer()

    game = FiveInRow(p1, p2)

    while game.tick():
        continue

if __name__ == "__main__":
    main()
