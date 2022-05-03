import unittest
from io import StringIO

import ssv

SAMPLE_SSV = """A\x1f\tB\x1f\tC\x1e
"A fox", said the bear.\nHow nice.\x1f\t1.4\x1f\t\tD\tC\tE\x1e
BLah\x1f\t\x1f\t\n\t"'\\\x1e
"""


class SsvTest(unittest.TestCase):
    def test_reader(self):
        input = StringIO(SAMPLE_SSV)
        reader = ssv.reader(input)
        resp = list(reader)
        self.assertSequenceEqual(
            resp,
            [
                ["A", "B", "C"],
                [""""A fox", said the bear.\nHow nice.""", "1.4", "\tD\tC\tE"],
                ["BLah", "", "\n\t\"'\\"],
            ],
        )

    def test_writer(self):
        out = StringIO()
        writer = ssv.writer(out)
        writer.writerow(["A", "B", "C"])
        writer.writerows(
            [
                [""""A fox", said the bear.\nHow nice.""", "1.4", "\tD\tC\tE"],
                ["BLah", "", "\n\t\"'\\"],
            ]
        )
        self.assertEqual(out.getvalue(), SAMPLE_SSV)

    def test_reader_compact(self):
        input = StringIO(SAMPLE_SSV)
        reader = ssv.reader(input, is_compact=True)
        resp = list(reader)
        self.assertSequenceEqual(
            resp,
            [
                ["A", "\tB", "\tC"],
                ["""\n"A fox", said the bear.\nHow nice.""", "\t1.4", "\t\tD\tC\tE"],
                ["\nBLah", "\t", "\t\n\t\"'\\"],
                ["\n"],
            ],
        )

    def test_writer_compact(self):
        out = StringIO()
        writer = ssv.writer(out, is_compact=True)
        writer.writerow(["A", "B", "C"])
        writer.writerows(
            [
                ["1", "3.14159", "\t"],
                ["Foo\n", "Dog", ""],
            ]
        )
        self.assertEqual(
            out.getvalue(), "A\x1fB\x1fC\x1e1\x1f3.14159\x1f\t\x1eFoo\n\x1fDog\x1f\x1e"
        )

    def test_read_mising_final_delimiter(self):
        input = StringIO("A\x1f\tB\x1e\nC\x1f\tD")
        reader = ssv.reader(input)
        self.assertSequenceEqual(
            list(reader),
            [
                ["A", "B"],
                ["C", "D"],
            ],
        )
