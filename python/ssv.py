from collections.abc import Iterator
from typing import Dict, Iterable, List, Sequence, TextIO, Tuple

CHUNK_SIZE = 4096


def _separators(is_compact: bool) -> Tuple[str, str]:
    """Return the record separator and field separator to use.
    If is_compact is true, don't include whitespace for readability.
    """
    if is_compact:
        return "\x1e", "\x1f"
    else:
        return "\n\x1e", "\t\x1f"


def reader(ssvfile: TextIO, is_compact=False) -> Iterator[List[str]]:
    """Create a reader of SSV Files

    Create a reader of SSV files that yields each record (row) as a list of
    strings containing the fields of that record.

    :ssvfile: A file-like object to read the SSV file from
    :is_compact:
        If true, use the "compact" form of SSV that doesn't include whitespace
        in the delemiters.
    """
    rs, fs = _separators(is_compact)
    buffer = ""
    while True:
        chunk = ssvfile.read(CHUNK_SIZE)
        if len(chunk) == 0:
            return buffer.split(fs)
        buffer = buffer + chunk
        records = buffer.split(rs)
        if len(records) < 2:
            continue
        for rec in records[:-1]:
            yield rec.split(fs)
        buffer = records[-1]


class Writer:
    def __init__(self, ssvfile: TextIO, is_compact=False):
        self._file = ssvfile
        self.rs, self.fs = _separators(is_compact)

    def writerow(self, row: Iterable[str]):
        self._file.write(self.fs.join(row))
        self._file.write(self.rs)

    def writerows(self, rows: Iterable[Iterable[str]]):
        self._file.write(self.rs.join(self.fs.join(row) for row in rows))
        self._file.write(self.rs)


def writer(ssvfile: TextIO, is_compact: bool):
    return Writer(ssvfile, is_compact)


class DictReader:
    fieldnames: Sequence[str]

    def __init__(
        self,
        f,
        fieldnames: Sequence[str] = None,
        restkey: str = "_rest",
        restval: str = None,
        *args,
        **kvs,
    ):
        self.reader = reader(f, *args, **kvs)
        if fieldnames is None:
            self.fieldnames = next(self.reader)
        else:
            self.fieldnames = fieldnames
        self.restkey = restkey
        self.restval = restval

    def __next__(self) -> dict:
        res: dict = {}
        row = next(self.reader)
        for i, name in enumerate(self.fieldnames):
            if i < len(row):
                res[name] = row[i]
            else:
                res[name] = self.restval or ""

        if i >= len(row):
            res[self.restkey] = row[i:]
        return res


class DictWriter:
    def __init__(
        self,
        f,
        fieldnames: Sequence[str],
        default_val: str = "",
        extrasaction="raise",
        *args,
        **kvs,
    ):
        self.fieldnames = fieldnames
        self.default_val = ""
        if extrasaction not in ("raise", "ignore"):
            raise ValueError(
                f"extrasaction {extrasaction} must be" "'raise' or 'ignore'"
            )
        self.extrasaction = extrasaction
        self.writer = writer(f, *args, **kvs)

    def writeheader(self):
        # write SOH character?
        self.writer.writerow(self.fieldnames)

    def writerow(self, row: Dict[str, str]):
        self.writer.writerow(self._dict_to_row(row))

    def writerows(self, rows: Iterable[Dict[str, str]]):
        self.writer.writerows(map(self._dict_to_row, rows))

    def _dict_to_row(self, d: Dict[str, str]) -> Iterator[str]:
        if self.extrasaction == "raise":
            wrong_fields = d.keys() - self.fieldnames
            if wrong_fields:
                raise ValueError(
                    "dict contains fields not in fieldnames: "
                    ", ".join(repr(f) for f in wrong_fields)
                )
        return (d.get(k, self.default_val) for k in self.fieldnames)
