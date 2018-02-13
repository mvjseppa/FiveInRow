#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication, QMessageBox
from FiveInRow import FiveInRow
from FiveInRowPlayers import FiveInRowPlayer
from MinimaxPlayer import MinimaxPlayer
from time import sleep

class FiveInRowCell(QPushButton):
    def __init__(self, txt, x, y):
        super().__init__(txt)
        self.x = x
        self.y = y

    def getCoordinates(self):
        return (self.y, self.x)

class FiveInRowGui(QWidget):
    startSignal = pyqtSignal()
    endSignal = pyqtSignal(int)

    def __init__(self):

        super().__init__()

        self.startSignal.connect(self.constructBoard)
        self.endSignal.connect(self.endGame)

        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.setLayout(self.grid)

        self.player = None
        self.move = None

        self.setWindowTitle('FiveInRow')
        self.show()

        self.symbols = [' ', 'X', 'O']
        self.colors = ['black', 'red', 'blue']

    def colorToStyle(self, color):
        return 'QPushButton {color: ' + color + '; font-size: 24pt;}'

    def cellClicked(self):
        if self.move is None:
            self.move = self.sender().getCoordinates()
        if self.player is not None:
            idx = self.player.number
            self.sender().setText(self.symbols[idx])
            self.sender().setStyleSheet(self.colorToStyle(self.colors[idx]))
        print(self.move)

    def startTurn(self, player):
        #self.constructBoard(board)
        self.move = None
        self.player = player
        self.startSignal.emit()

    def getMove(self):
        return self.move

    def endGame(self, winner):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        txt = "It's a draw!" if winner == 0 else "Player" + winner + " wins!"
        msg.setText(txt)
        msg.setWindowTitle(txt)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(msg.close)

        msg.exec_()

    def constructBoard(self):
        if self.player is None:
            return

        for x,row in enumerate(self.player.game.board):
            for y,cell in enumerate(row):

                cellButton = FiveInRowCell(self.symbols[cell], x, y)
                cellButton.setFixedSize(50,50)
                cellButton.setStyleSheet(self.colorToStyle(self.colors[cell]))
                cellButton.clicked.connect(self.cellClicked)
                self.grid.addWidget(cellButton, x, y)

class QtPlayer(FiveInRowPlayer):
    def __init__(self, gui):
        super().__init__()
        self.gui = gui

    def requestMove(self):
        self.gui.startTurn(self)
        move = None
        while move is None:
            sleep(0.2)
            move = self.gui.getMove()
        return move

    def notifyWin(self):
        self.gui.endSignal.emit(self.number)

    def notifyLoss(self):
        pass

    def notifyDraw(self):
        if self.number == 1:
            self.gui.endSignal.emit(0)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    gamegui = FiveInRowGui()

    p1 = QtPlayer(gamegui)
    #p2 = QtPlayer(gamegui)
    p2 = MinimaxPlayer(5)

    game = FiveInRow(p1, p2)
    game.start()

    sys.exit(app.exec_())
    game.join()
