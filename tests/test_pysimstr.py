import unittest
import pysimstr


class TestSimStr(unittest.TestCase):

    def test_make_unique_ngrams(self):
        self.assertEqual({'Ban', 'ana', 'nan'},
                         pysimstr.make_unique_ngrams('Banana', 3))
        self.assertEqual({'b', 'a', 'n'},
                         pysimstr.make_unique_ngrams('banana', 1))

    def test_db_init(self):
        db = pysimstr.SimStr(cutoff=0.8, idx_size=3, plus_minus=2)
        self.assertEqual(db.idx_size, 3)
        self.assertEqual(db.plus_minus, 2)
        self.assertEqual(db.cutoff, 0.8)

    def test_db_compare_custom(self):
        db = pysimstr.SimStr(
            cutoff=0.8, idx_size=1, plus_minus=1,
            comparison_func=lambda x, y: 1 - (abs(len(x) - len(y)) / 100))
        db.insert(['STRING1', 'STRING2'])
        self.assertEqual(db.check('STRING3'[::-1]), True)
        self.assertEqual(db.check('STRING333'), False)

    def test_db_compare_custom2(self):
        db = pysimstr.SimStr(
            cutoff=0.8, idx_size=4, plus_minus=1,
            comparison_func=lambda x, y: 1 - (abs(len(x) - len(y)) / 100))
        db.insert(['STRING1', 'STRING2'])
        self.assertEqual(db.check('STRING'[::-1]), False)

    def test_db_compare_default(self):
        db = pysimstr.SimStr()
        db.insert(['Pizza', 'Sausage'])
        self.assertEqual(db.retrieve('pizza'), ['Pizza'])
        self.assertEqual(db.check('Notpizza'), False)

    def test_retrieve_with_score(self):
        db = pysimstr.SimStr(
            comparison_func=lambda x, y: 1 - (abs(len(x) - len(y)) / 100))
        db.insert(['SomeSTRING'])
        result = db.retrieve_with_score('SomeOTHER1')
        self.assertAlmostEqual(result[0][1], 1)

if __name__ == '__main__':
    unittest.main()
