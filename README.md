# CRISPRMatch

CRISPRMatch is a Qt desktop application and a set of NGS utilities for
high-throughput CRISPR genome-editing analysis. This repository packages the
original GUI as an installable Python project and adds a dual-barcode FASTQ
demultiplexer and reproducible conda environment.

## Origin, authors, and downstream modifications

The original project is
[zhangtaolab/CRISPRMatchGUI](https://github.com/zhangtaolab/CRISPRMatchGUI).
Its Git history identifies `qyou <youqi@yzu.edu.cn>` as the original author,
with the repository hosted by `zhangtaolab` and the original commits dated
2018-09-03.

This downstream release is maintained by `xiettiansong`. The downstream work
includes:

- WSL/Linux installation and a unified conda environment;
- dual-barcode FASTQ demultiplexing, including reverse-complement handling for
  `Barcode_R` and `.gz` input;
- migration from `pyfasta` to `pyfaidx`;
- package-relative Qt resource lookup;
- formal `crisprmatch`, `crisprmatch-split`, and `crisprmatch-merge` commands;
- safer FLASH process execution and log capture;
- input validation, automated tests, synthetic examples, and release
  documentation;
- removal of caches, generated results, real sequencing files, and local
  machine configuration from the release.

See [NOTICE.md](NOTICE.md) for the important upstream licensing status. No
explicit license was found in the checked-out upstream repository; obtain
permission before making this derivative repository public.

## Supported environment

- Linux, or Windows 11 with WSL2/WSLg
- x86-64 conda-compatible system
- A graphical session for the Qt interfaces

The provided environment installs Python 3.11, BWA 0.7.17, samtools 1.19,
FLASH 1.2.11, PyQt 5.15, and all Python dependencies into one environment.

## Installation

Install Miniforge, Miniconda, or Mambaforge first. Then clone this repository
and run:

```bash
git clone https://github.com/YOUR_ACCOUNT/CRISPRMatch.git
cd CRISPRMatch
conda env create -f environment.yml
conda activate crisprmatch
```

The editable package installation is included in `environment.yml`. Verify the
installation with:

```bash
crisprmatch --version
crisprmatch-split --help
crisprmatch-merge --help
python -c "import crisprmatch; print(crisprmatch.__version__)"
bwa 2>&1 | head
samtools --version | head
flash --version
pytest
```

## Commands

```bash
crisprmatch          # Main CRISPR editing analysis GUI
crisprmatch-split    # Dual-barcode FASTQ demultiplexing GUI
crisprmatch-merge    # Paired-end merging GUI backed by FLASH
```

On Windows, run these inside the WSL distribution. WSLg normally displays the
Qt windows without installing a separate X server.

## Barcode demultiplexing

The barcode table must contain these columns:

```csv
Sample,Barcode_L,Barcode_R
sample_A,ACGT,AGTC
```

Matching behavior is preserved from the downstream optimized splitter:

1. `Barcode_L` is matched directly.
2. `Barcode_R` is reverse-complemented before matching.
3. Both processed barcodes may occur anywhere in the read sequence.
4. When more than one pair matches, the first row in the table wins.
5. Output reads are not barcode-trimmed.
6. Unmatched reads are written to `unmatched.fastq`.

The splitter rejects missing columns, missing values, invalid DNA symbols,
duplicate sample names, duplicate barcode pairs, unsafe sample names, and
malformed FASTQ records. Input may be plain FASTQ or gzip-compressed FASTQ;
output is plain FASTQ.

Tiny synthetic input files are provided in `examples/`. Real sequencing files
and private barcode sheets are intentionally excluded.

## Main analysis inputs

The legacy analysis GUI expects:

- a target-region FASTA file;
- a sample information CSV;
- a group information CSV;
- a directory containing sample FASTQ data in the layout expected by the
  original CRISPRMatch workflow.

BWA and samtools are discovered from the active conda environment. Activate
`crisprmatch` before launching any command.

## Development and tests

```bash
conda activate crisprmatch
pip install -e ".[test]"
pytest
pytest -m integration
```

The regular test suite covers barcode validation, reverse-complement logic,
plain and gzip FASTQ splitting, malformed FASTQ detection, FASTA access, Qt
resource lookup, and importability. Integration tests verify that BWA,
samtools, and FLASH are supplied by the active environment.

## Preparing a public release

Before publishing:

1. Obtain permission from the upstream copyright holder or add an agreed
   upstream license.
2. Replace `YOUR_ACCOUNT` in this README with the final GitHub account.
3. Replace the maintainer handle with the desired formal name/contact details.
4. Run `pytest` and `pytest -m integration` in a freshly created environment.
5. Review `git status` to ensure no FASTQ, BAM, barcode, result, or local
   configuration files are staged.
6. Tag the release, for example `git tag -a v0.1.0 -m "CRISPRMatch 0.1.0"`.

## Citation

Until a formal paper or software citation is supplied, cite the original
repository and clearly identify this downstream release/version. Add a
`CITATION.cff` after confirming the preferred author list and citation details.
