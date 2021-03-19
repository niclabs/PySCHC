"""test_integrity_check: Integrity Check Unit Test"""

from unittest import TestCase, main
from schc_messages.schc_header import IntegrityCheck


class TestIntegrityCheck(TestCase):

    def setUp(self) -> None:
        """
        Sets up unit test

        Returns
        -------
        None
        """
        self.c = IntegrityCheck(True)
        self.not_c = IntegrityCheck(False)

    def test_size(self) -> None:
        self.assertEqual(1, self.c.size, "Wrong Size of IC")
        self.assertEqual(1, self.not_c.size, "Wrong Size of Not IC")

    def test_as_bits(self) -> None:
        self.assertEqual("1", self.c.as_bits(), "IC bits wrong mapped")
        self.assertEqual("0", self.not_c.as_bits(), "Not IC bits wrong mapped")

    def test_format_text(self) -> None:
        self.assertEqual(
            (" 1 ", " C ", " 1 "),
            self.c.format_text(),
            "Wrong text generated for IC"
        )
        self.assertEqual(
            (" 1 ", " C ", " 0 "),
            self.not_c.format_text(),
            "Wrong text generated for Not IC"
        )


if __name__ == '__main__':
    main()
