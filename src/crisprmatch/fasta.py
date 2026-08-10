"""Small compatibility layer replacing the unmaintained ``pyfasta`` package."""

from pathlib import Path

from pyfaidx import Fasta as _PyfaidxFasta


class Fasta:
    """Expose the subset of the old ``pyfasta.Fasta`` API used by CRISPRMatch.

    ``as_raw=True`` makes record indexing and slicing return ordinary strings,
    matching the behavior expected by the legacy analysis modules.
    """

    def __init__(self, filename):
        self.filename = str(Path(filename))
        self._fasta = _PyfaidxFasta(
            self.filename,
            as_raw=True,
            sequence_always_upper=False,
        )

    def __getitem__(self, key):
        return self._fasta[key]

    def keys(self):
        return self._fasta.keys()

    def close(self):
        self._fasta.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
