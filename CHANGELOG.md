# Changelog

## 0.1.0

- Reorganized the application as an installable `src/`-layout Python package.
- Added `crisprmatch`, `crisprmatch-split`, and `crisprmatch-merge` commands.
- Added one conda environment containing BWA, samtools, FLASH, Qt, Python, and
  all Python dependencies.
- Replaced unmaintained, Python-2-era `pyfasta` with `pyfaidx` through a small
  compatibility layer.
- Made Qt `.ui` lookup independent of the current working directory.
- Extracted dual-barcode FASTQ demultiplexing into a validated, testable module.
- Added gzip FASTQ input support, malformed-record checks, and summary counts.
- Replaced shell-composed FLASH execution with an argument-list subprocess.
- Excluded real sequencing data, generated files, caches, and local settings.
- Added synthetic examples, pytest coverage, and a conda-based CI workflow.
- Added the 192-entry `7. Com_barcode_primer for Hi-Tom.csv` table as a
  directly loadable barcode reference under `examples/`.
