"""Qt interface for CRISPRMatch dual-barcode FASTQ demultiplexing."""

import sys
from pathlib import Path

import pandas as pd
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog

from crisprmatch.CMlib.show_barcodestable import showtable as BarcodeTable
from crisprmatch.demultiplex import efficient_splitter_dual_barcode
from crisprmatch.resources import ui_path


UiSplitDialog, _ = uic.loadUiType(ui_path("split_lanes.ui"))


class SplitDialog(QtWidgets.QDialog, UiSplitDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Split FASTQ")
        self.resize(500, 400)

        self.fastq_path = None
        self.barcode_path = None
        self.output_path = None
        self.barcode_dialog = None

        self.fastqline.setReadOnly(True)
        self.barcodeline.setReadOnly(True)
        self.outputline.setReadOnly(True)
        self.fastqbtn.clicked.connect(self.select_fastq)
        self.barcodebtn.clicked.connect(self.select_barcodes)
        self.outputbtn.clicked.connect(self.select_output)
        self.showbtn.clicked.connect(self.show_barcodes)
        self.splitbtn.clicked.connect(self.split_fastq)
        self.resetbtn.clicked.connect(self.reset)

    def select_fastq(self):
        selected, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open FASTQ file",
            str(Path.cwd()),
            "FASTQ files (*.fastq *.fq *.fastq.gz *.fq.gz);;All files (*)",
        )
        if selected:
            self.fastq_path = selected
            self.fastqline.setText(selected)

    def select_barcodes(self):
        selected, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open barcode table",
            str(Path.cwd()),
            "Tables (*.csv *.tsv *.txt);;All files (*)",
        )
        if not selected:
            return
        try:
            self.barcode_df = pd.read_csv(selected, sep=None, engine="python")
        except Exception as error:
            self.show_warning("Cannot read barcode table", str(error))
            return
        self.barcode_path = selected
        self.barcode_dialog = None
        self.barcodeline.setText(selected)

    def select_output(self):
        selected = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select output directory", str(Path.cwd())
        )
        if selected:
            self.output_path = selected
            self.outputline.setText(selected)

    def show_barcodes(self):
        if not self.barcode_path:
            self.show_warning("Barcode table required", "Load a barcode table first.")
            return
        self.barcode_dialog = BarcodeTable()
        if self.barcode_dialog.setuptable(self.barcode_df) == "yes":
            self.barcode_dialog.show()

    def reset(self):
        self.fastq_path = None
        self.barcode_path = None
        self.output_path = None
        self.barcode_dialog = None
        self.fastqline.clear()
        self.barcodeline.clear()
        self.outputline.clear()

    def split_fastq(self):
        if not self.fastq_path:
            self.show_warning("FASTQ required", "Load a FASTQ file first.")
            return
        if not self.barcode_dialog:
            self.show_warning(
                "Barcode confirmation required",
                "Click Show, review the barcode table, and click Confirm first.",
            )
            return
        if not self.output_path:
            self.show_warning("Output required", "Select an output directory first.")
            return

        confirmed, barcode_df = self.barcode_dialog.resulttest()
        if confirmed != "yes":
            self.show_warning("Barcode confirmation required", "Click Confirm first.")
            return

        self.show_progress("Preparing demultiplexing...")
        try:
            summary = efficient_splitter_dual_barcode(
                barcode_df=barcode_df,
                fastq_path=self.fastq_path,
                output_dir=self.output_path,
            )
        except Exception as error:
            self.show_warning("Demultiplexing failed", str(error))
            return

        QtWidgets.QMessageBox.information(
            self,
            "Finished",
            (
                f"Processed {summary.total_records:,} reads.\n"
                f"Matched: {summary.matched_records:,}\n"
                f"Unmatched: {summary.unmatched_records:,}"
            ),
        )

    def show_warning(self, title, message):
        QtWidgets.QMessageBox.warning(self, title, message)

    def show_progress(self, message):
        progress = QProgressDialog(message, None, 0, 0, self)
        progress.setWindowTitle("CRISPRMatch")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        QtWidgets.QApplication.processEvents()
        progress.close()


# Compatibility with code that imported the old class name.
showtable = SplitDialog


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = SplitDialog()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
