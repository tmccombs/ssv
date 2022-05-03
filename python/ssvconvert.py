#!/usr/bin/env python3
import csv
from typing import TextIO

import ssv


def csv_to_ssv(
    source: TextIO, dest: TextIO, *, ssv_compact: bool = False, **csv_params
):
    """Read a CSV from ``csv`` and write it as an SSV to ``ssv``

    If ``ssv_compact`` is ``True``, then use the "compact" delimiters for SSV.
    ``csv_params`` are passed through to |csv.reader|_.

    .. |csv.reader| replace:: ``csv.reader``
    .. _csv.reader: https://docs.python.org/3/library/csv.html#csv.reader
    """
    writer = ssv.writer(dest, ssv_compact)
    for row in csv.reader(source, **csv_params):
        writer.writerow(row)


def ssv_to_csv(
    source: TextIO, dest: TextIO, *, ssv_compact: bool = False, **csv_params
):
    """TODO"""
    writer = csv.writer(dest, **csv_params)
    for row in ssv.reader(source, ssv_compact):
        writer.writerow(row)


if __name__ == "__main__":
    import argparse
    import sys

    def csv_quoting(v: str):
        if v == 'all':
            return csv.QUOTE_ALL
        elif v == 'minimal':
            return csv.QUOTE_MINIMAL
        elif v == 'nonnumeric':
            return csv.QUOTE_NONNUMERIC
        elif v == 'none':
            return csv.QUOTE_NONE
        else:
            raise ValueError(v)

    parser = argparse.ArgumentParser(description="Convert between CSV and SSV")
    parser.add_argument(
        "--compact-ssv",
        "-c",
        dest="ssv_compact",
        help="Use compact delimiters for SSV",
        action="store_true",
    )
    parser.add_argument(
        "--csv-dialect", "-d", dest="dialect", help="CSV dialect to use"
    )
    parser.add_argument(
        "--csv-delimiter", "-D", dest="delimiter", help="CSV field delimiter to use"
    )
    parser.add_argument("--escapechar", "-e", help="Escape character for CSV")
    parser.add_argument("--quotechar", "-q", help="Quote character for CSV")
    parser.add_argument(
        "--doublequote",
        "-X",
        help="Allow escaping quote character by repeating it inside quotes",
        action="store_true",
    )
    parser.add_argument(
        "--csv-skip-space",
        "-w",
        dest="skipinitialspace",
        help="Skip whitespace immediately following delimiter in CSV",
        action="store_true",
    )
    parser.add_argument(
        "--csv-strict",
        "-s",
        dest="strict",
        help="Raise an error on bad CSV input",
        action="store_true",
    )
    parser.add_argument(
        "--quoting",
        "-l",
        type=csv_quoting,
        metavar='{all,minimal,nonnumeric,none}',
        help="Specify when to quote",
    )
    parser.add_argument(
        "command",
        choices=["to-csv", "from-csv"],
        help="Specify whether converting to or from CSV",
    )

    args = parser.parse_args()
    command = args.command
    params = {k: v for k, v in vars(args).items() if v is not None and k != "command"}
    # For now, just use stdin/stdout. Maybe in the future allow passing filenames
    # as arguments.
    if command == "to-csv":
        ssv_to_csv(sys.stdin, sys.stdout, **params)
    elif command == "from-csv":
        csv_to_ssv(sys.stdin, sys.stdout, **params)
    else:
        print(f"Unsupported command {command}", file=sys.stderr)
        exit(1)
