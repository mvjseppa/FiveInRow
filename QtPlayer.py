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
    endSignal = pyqtSignal(bool)

    def __init__(self):

        super().__init__()

        self.startSignal.connect(self.constructBoard)
        self.endSignal.connect(self.endGame)

        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.setLayout(self.grid)

        self.board = None
        self.move = None

        self.setWindowTitle('FiveInRow')
        self.show()


    def cellClicked(self):
        if self.move is None:
            self.move = self.sender().getCoordinates()
        print(self.move)

    def startTurn(self, board):
        #self.constructBoard(board)
        self.move = None
        self.board = board
        self.startSignal.emit()

    def getMove(self):
        return self.move

    def endGame(self, didWin):
        msg = QMessageBox()

        icon = QMessageBox.Information if didWin else QMessageBox.Critical
        msg.setIcon(icon)

        txt = "You win!" if didWin else "You lost!"
        msg.setText(txt)
        msg.setWindowTitle(txt)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(msg.close)

        msg.exec_()

    def constructBoard(self):
        if self.board is None:
            return

        symbols = [' ', 'X', 'O']
        styles = [
            'QPushButton {color: black; font-size: 24pt;}',
            'QPushButton {color: red; font-size: 24pt;}',
            'QPushButton {color: blue; font-size: 24pt;}',
        ]

        for x,row in enumerate(self.board):
            for y,cell in enumerate(row):

                cellButton = FiveInRowCell(symbols[cell], x, y)
                cellButton.setFixedSize(50,50)
                cellButton.setStyleSheet(styles[cell])
                cellButton.clicked.connect(self.cellClicked)
                self.grid.addWidget(cellButton, x, y)

class QtPlayer(FiveInRowPlayer):
    def __init__(self, gui):
        super().__init__()
        self.gui = gui

    def requestMove(self):
        self.gui.startTurn(self.game.board)
        move = None
        while move is None:
            sleep(0.2)
            move = self.gui.getMove()
        return move

    def notifyWin(self):
        self.gui.endSignal.emit(True)

    def notifyLoss(self):
        self.gui.endSignal.emit(False)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    gamegui = FiveInRowGui()

    p1 = QtPlayer(gamegui)
    p2 = MinimaxPlayer(3)

    game = FiveInRow(p1, p2)

    game.start()


    sys.exit(app.exec_())
    game.join()
