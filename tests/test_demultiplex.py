import gzip
from pathlib import Path

import pandas as pd
import pytest

from crisprmatch.demultiplex import (
    demultiplex_fastq,
    reverse_complement,
    validate_barcode_table,
)


FASTQ = """@matched
TTACGTAAAAGACTCC
+
IIIIIIIIIIIIIIII
@unmatched
TTTTTTTTTTTTTTTT
+
IIIIIIIIIIIIIIII
"""


def barcode_table():
    return pd.DataFrame(
        {"Sample": ["sample_A"], "Barcode_L": ["ACGT"], "Barcode_R": ["AGTC"]}
    )


def count_records(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines()) // 4


@pytest.mark.parametrize("compressed", [False, True])
def test_demultiplexes_plain_and_gzip_fastq(tmp_path, compressed):
    input_path = tmp_path / ("input.fastq.gz" if compressed else "input.fastq")
    if compressed:
        with gzip.open(input_path, "wt", encoding="utf-8") as handle:
            handle.write(FASTQ)
    else:
        input_path.write_text(FASTQ, encoding="utf-8")

    output_dir = tmp_path / "output"
    summary = demultiplex_fastq(barcode_table(), input_path, output_dir)

    assert summary.total_records == 2
    assert summary.matched_records == 1
    assert summary.unmatched_records == 1
    assert summary.sample_counts == {"sample_A": 1}
    assert count_records(output_dir / "sample_A.fastq") == 1
    assert count_records(output_dir / "unmatched.fastq") == 1


def test_reverse_complement_normalizes_case_and_whitespace():
    assert reverse_complement(" agtc ") == "GACT"


@pytest.mark.parametrize("barcode", ["", "AXGT", "AC-GT"])
def test_reverse_complement_rejects_invalid_barcodes(barcode):
    with pytest.raises(ValueError, match="Invalid DNA barcode"):
        reverse_complement(barcode)


def test_validation_rejects_duplicate_samples():
    table = pd.DataFrame(
        {
            "Sample": ["same", "same"],
            "Barcode_L": ["AAAA", "CCCC"],
            "Barcode_R": ["GGGG", "TTTT"],
        }
    )
    with pytest.raises(ValueError, match="Sample names must be unique"):
        validate_barcode_table(table)


def test_validation_rejects_missing_columns():
    with pytest.raises(ValueError, match="missing required columns"):
        validate_barcode_table(pd.DataFrame({"Sample": ["sample_A"]}))


def test_truncated_fastq_is_rejected(tmp_path):
    input_path = tmp_path / "broken.fastq"
    input_path.write_text("@read\nACGT\n+\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Incomplete FASTQ record"):
        demultiplex_fastq(barcode_table(), input_path, tmp_path / "output")
