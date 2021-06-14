"""test_rcs: Reassembly Check Sequence Unit Test"""

from unittest import TestCase, main
from schc_messages.schc_header import ReassemblyCheckSequence


class TestRCS(TestCase):

    def setUp(self) -> None:
        """
        Sets up unit test

        Returns
        -------
        None
        """
        # self.rcs = ReassemblyCheckSequence()

    def test_wrong_fcn_size(self) -> None:
        self.assertTrue(True)

    def test_size(self) -> None:
        self.assertTrue(True)

    def test_as_bits(self) -> None:
        self.assertTrue(True)

    def test_format_text(self) -> None:
        self.assertTrue(True)


if __name__ == '__main__':
    main()
