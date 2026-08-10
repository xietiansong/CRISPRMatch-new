"""FASTQ demultiplexing by a left barcode and reverse-complemented right barcode."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass
import gzip
from pathlib import Path
import re

import pandas as pd


REQUIRED_COLUMNS = ("Sample", "Barcode_L", "Barcode_R")
DNA_RE = re.compile(r"^[ACGTN]+$", re.IGNORECASE)


@dataclass(frozen=True)
class DemultiplexSummary:
    total_records: int
    matched_records: int
    unmatched_records: int
    sample_counts: dict[str, int]


def reverse_complement(sequence: str) -> str:
    """Return the reverse complement of an A/C/G/T/N sequence."""
    sequence = str(sequence).strip().upper()
    if not sequence or not DNA_RE.fullmatch(sequence):
        raise ValueError(f"Invalid DNA barcode: {sequence!r}")
    return sequence.translate(str.maketrans("ACGTN", "TGCAN"))[::-1]


def validate_barcode_table(barcode_df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize the table consumed by the demultiplexer."""
    missing = [column for column in REQUIRED_COLUMNS if column not in barcode_df.columns]
    if missing:
        raise ValueError(f"Barcode table is missing required columns: {', '.join(missing)}")

    normalized = barcode_df.loc[:, REQUIRED_COLUMNS].copy()
    if normalized.empty:
        raise ValueError("Barcode table contains no samples")
    if normalized.isna().any().any():
        raise ValueError("Barcode table contains missing Sample or barcode values")

    for column in REQUIRED_COLUMNS:
        normalized[column] = normalized[column].astype(str).str.strip()

    if (normalized["Sample"] == "").any():
        raise ValueError("Sample names cannot be empty")
    invalid_names = normalized["Sample"].map(
        lambda value: value in {".", ".."} or "/" in value or "\\" in value
    )
    if invalid_names.any():
        raise ValueError("Sample names cannot contain path separators")
    if normalized["Sample"].duplicated().any():
        raise ValueError("Sample names must be unique")

    for column in ("Barcode_L", "Barcode_R"):
        normalized[column] = normalized[column].str.upper()
        invalid = ~normalized[column].map(lambda value: bool(DNA_RE.fullmatch(value)))
        if invalid.any():
            raise ValueError(f"Column {column} contains an invalid DNA barcode")

    if normalized[["Barcode_L", "Barcode_R"]].duplicated().any():
        raise ValueError("Barcode pairs must be unique")
    return normalized


def _open_fastq(path: Path):
    if path.name.lower().endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="strict")
    return path.open("rt", encoding="utf-8", errors="strict")


def demultiplex_fastq(
    barcode_df: pd.DataFrame,
    fastq_path,
    output_dir,
) -> DemultiplexSummary:
    """Split a FASTQ file using the downstream CRISPRMatch barcode convention.

    ``Barcode_L`` is matched directly and ``Barcode_R`` is reverse-complemented
    before matching. Both sequences may occur anywhere in the read. The first
    matching barcode pair in table order wins, and reads are written untrimmed.
    """
    barcodes = validate_barcode_table(barcode_df)
    fastq_path = Path(fastq_path)
    output_dir = Path(output_dir)
    if not fastq_path.is_file():
        raise FileNotFoundError(f"FASTQ input does not exist: {fastq_path}")
    output_dir.mkdir(parents=True, exist_ok=True)

    prepared = [
        (row.Sample, row.Barcode_L, reverse_complement(row.Barcode_R))
        for row in barcodes.itertuples(index=False)
    ]
    sample_counts = {sample: 0 for sample, _, _ in prepared}
    total_records = 0
    matched_records = 0

    with ExitStack() as stack:
        input_handle = stack.enter_context(_open_fastq(fastq_path))
        output_handles = {
            sample: stack.enter_context((output_dir / f"{sample}.fastq").open("wt", encoding="utf-8"))
            for sample in sample_counts
        }
        unmatched_handle = stack.enter_context(
            (output_dir / "unmatched.fastq").open("wt", encoding="utf-8")
        )

        while True:
            header = input_handle.readline()
            if not header:
                break
            sequence = input_handle.readline()
            separator = input_handle.readline()
            quality = input_handle.readline()
            total_records += 1
            if not sequence or not separator or not quality:
                raise ValueError(f"Incomplete FASTQ record at record {total_records}")
            if not header.startswith("@") or not separator.startswith("+"):
                raise ValueError(f"Malformed FASTQ record at record {total_records}")

            record = header + sequence + separator + quality
            sequence_upper = sequence.strip().upper()
            destination = unmatched_handle
            for sample, barcode_left, barcode_right_rc in prepared:
                if barcode_left in sequence_upper and barcode_right_rc in sequence_upper:
                    destination = output_handles[sample]
                    sample_counts[sample] += 1
                    matched_records += 1
                    break
            destination.write(record)

    return DemultiplexSummary(
        total_records=total_records,
        matched_records=matched_records,
        unmatched_records=total_records - matched_records,
        sample_counts=sample_counts,
    )


def efficient_splitter_dual_barcode(barcode_df, fastq_path, output_dir):
    """Backward-compatible GUI wrapper around :func:`demultiplex_fastq`."""
    summary = demultiplex_fastq(barcode_df, fastq_path, output_dir)
    print("\n--- 拆分完成 ---")
    print(f"总共处理记录: {summary.total_records:,}")
    print(f"成功匹配记录: {summary.matched_records:,}")
    print(f"未匹配记录: {summary.unmatched_records:,}")
    return summary
