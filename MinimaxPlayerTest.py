import unittest
from MinimaxPlayer import MinimaxPlayer

class MinimaxPlayerTest(unittest.TestCase):

    #scoreTable = [0, 1, 2, 10, 50, 10000, 10000]

    def test_evaluateLine(self):
        mp = MinimaxPlayer()
        mp.setMarks('O', 'X')
        self.assertTrue( mp.evaluateLine("........", True) == 0 )
        self.assertTrue( mp.evaluateLine("..X.....", True) == -2 )
        self.assertTrue( mp.evaluateLine("....XO.....", True) == -1 )

        scores = []
        scores.append( mp.evaluateLine("XX..XO..", True))
        scores.append( mp.evaluateLine(".XX..XO..", True))
        scores.append( mp.evaluateLine("XXX..O..", True))
        scores.append( mp.evaluateLine(".XXX..O..", True))
        scores.append( mp.evaluateLine("XXXXX", True))

        for i in range(len(scores)-1):
            print("round: ", i, scores[i], scores[i+1])
            self.assertTrue(scores[i] >= scores[i+1])

        self.assertTrue(mp.evaluateLine(".XXXXX.", True) == -20000)

        #self.assertTrue(
        print(mp.evaluateLine("..XOOO...XXX..", True) )

if __name__ == '__main__':
    unittest.main()
