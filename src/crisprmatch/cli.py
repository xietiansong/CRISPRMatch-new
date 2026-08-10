"""Console entry points that provide help/version output before loading Qt."""

import argparse
import sys

from crisprmatch import __version__


def _parser(program, description):
    parser = argparse.ArgumentParser(prog=program, description=description)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main():
    _parser("crisprmatch", "Launch the CRISPRMatch analysis GUI.").parse_args()
    from crisprmatch.main import main as launch

    return launch()


def split():
    _parser("crisprmatch-split", "Launch the dual-barcode FASTQ splitter.").parse_args()
    from crisprmatch.split_gui import main as launch

    return launch()


def merge():
    _parser("crisprmatch-merge", "Launch the FLASH paired-end read merger.").parse_args()
    from crisprmatch.merge_gui import main as launch

    return launch()


if __name__ == "__main__":
    sys.exit(main())
