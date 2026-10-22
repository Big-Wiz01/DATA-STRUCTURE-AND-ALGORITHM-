"""Unit tests for stack_evaluator.py  (run: python -m unittest -v test_stack_evaluator)"""
import unittest
from stack_evaluator import Stack, evaluate_expression


class TestStack(unittest.TestCase):
    def test_push_peek_pop(self):
        s = Stack()
        s.push(1); s.push(2)
        self.assertEqual(s.peek(), 2)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.pop(), 1)
        self.assertTrue(s.is_empty())

    def test_empty_stack_errors(self):
        s = Stack()
        with self.assertRaises(IndexError):
            s.pop()
        with self.assertRaises(IndexError):
            s.peek()


class TestEvaluation(unittest.TestCase):
    def test_brief_examples(self):
        self.assertEqual(evaluate_expression("3 + 5 * 2"), 13)
        self.assertEqual(evaluate_expression("(8 / 4) + 7 * 2"), 16)
        self.assertEqual(evaluate_expression("10 - (2 + 3) * 4"), -10)

    def test_precedence_and_associativity(self):
        self.assertEqual(evaluate_expression("100 - 20 - 30"), 50)
        self.assertEqual(evaluate_expression("2 + 3 * 4 - 6 / 2"), 11)

    def test_unary_and_decimals(self):
        self.assertEqual(evaluate_expression("-5 + 8"), 3)
        self.assertEqual(evaluate_expression("2 * -3"), -6)
        self.assertEqual(evaluate_expression("2.5 * 4"), 10)

    def test_nested_parentheses(self):
        self.assertEqual(evaluate_expression("((2 + 3) * (4 - 1)) / 5"), 3)

    def test_errors(self):
        for bad in ["8 / (4 - 4)", "(2 + 3", "2 + 3)", "2 + * 3", "4 $ 2", "", "5 +"]:
            with self.assertRaises(ValueError, msg=bad):
                evaluate_expression(bad)


if __name__ == "__main__":
    unittest.main()
