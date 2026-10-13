import unittest
from local_graph import build_graph

class GraphTests(unittest.TestCase):
    def setUp(self):
        self.graph = build_graph()
    def test_sum(self):
        self.assertEqual(self.graph.invoke({'x':2,'y':3,'operation':'sum'})['result'],5)
    def test_product_negative(self):
        self.assertEqual(self.graph.invoke({'x':-2,'y':3,'operation':'product'})['result'],-6)
    def test_zero(self):
        self.assertEqual(self.graph.invoke({'x':0,'y':3,'operation':'product'})['result'],0)
    def test_invalid_operation(self):
        with self.assertRaises(ValueError):
            self.graph.invoke({'x':2,'y':3,'operation':'divide'})
    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            self.graph.invoke({'x':'2','y':3,'operation':'sum'})
    def test_execution_order(self):
        updates=list(self.graph.stream({'x':2,'y':3,'operation':'sum'}))
        self.assertEqual([next(iter(update)) for update in updates],['validate','calculate'])

if __name__ == '__main__':
    unittest.main()
