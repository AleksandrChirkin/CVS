import os
import sys
import unittest
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from cvs import Init, Add, Commit, Reset, Log, Checkout, System  # noqa


class TestCommands(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_init(self) -> None:
        pass

    def test_add(self) -> None:
        pass

    def test_commit(self) -> None:
        pass

    def test_reset(self) -> None:
        pass

    def test_log(self) -> None:
        pass

    def test_checkout(self) -> None:
        pass

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
