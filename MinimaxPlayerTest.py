import unittest
from MinimaxPlayer import MinimaxPlayer, MinimaxStatus

class MinimaxPlayerTest(unittest.TestCase):

    #scoreTable = [0, 1, 2, 10, 50, 10000, 10000]

    def test_evaluateLine(self):
        mp = MinimaxStatus("     ",None, None)

        self.assertTrue( mp.evaluateLine("000000000") == 0 )
        self.assertTrue( mp.evaluateLine("0001001100") == 0 )
        self.assertTrue( mp.evaluateLine("001110000") == 1 )
        self.assertTrue( mp.evaluateLine("00111001110000") == 2 )
        self.assertTrue( mp.evaluateLine("0011110000") == 10 )
        self.assertTrue( mp.evaluateLine("00111011110000") == 11 )
        self.assertTrue( mp.evaluateLine("001111100000") == 10000)

        self.assertTrue( mp.evaluateLine("0002001100") == 0 )
        self.assertTrue( mp.evaluateLine("0022200000") == -1 )
        self.assertTrue( mp.evaluateLine("0022200111000") == 0 )
        self.assertTrue( mp.evaluateLine("002222001110") == -9 )
        self.assertTrue( mp.evaluateLine("002222100000") == 0 )
        self.assertTrue( mp.evaluateLine("0012222210001110") == -10000)


    def test_diagonalStart(self):
        ms = MinimaxStatus("     ",None,None)

        self.assertTrue(ms.diagonalStartingPoints(1,3) == ((0,2),(4,0)))
        self.assertTrue(ms.diagonalStartingPoints(3,2) == ((1,0),(4,1)))
        self.assertTrue(ms.diagonalStartingPoints(1,2) == ((0,1),(3,0)))
        self.assertTrue(ms.diagonalStartingPoints(3,1) == ((2,0),(4,0)))
        self.assertTrue(ms.diagonalStartingPoints(3,3) == ((0,0),(4,2)))

        ms = MinimaxStatus("        ",None,None)
        self.assertTrue(ms.diagonalStartingPoints(3,2) == ((1,0),(5,0)))

    def test_statusUpdate(self):

        board = [
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,1,0,0,0,0],
            [0,0,0,0,1,0,0,0],
            [0,0,0,0,0,1,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,2,2,2,0,0,0],
            [0,0,0,0,0,0,0,0]
        ]

        print(''.join([str(item) for item in board[2]]))

        ms = MinimaxStatus(board, set(), 0)

        ms.update(2,1,1)
        self.assertTrue(ms.score == 9)

        ms.update(5,6,2)
        print("score:", ms.score)
        self.assertTrue(ms.score == 0)

if __name__ == '__main__':
    unittest.main()
