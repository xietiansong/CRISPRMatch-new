"""Qt interface for merging paired-end reads with FLASH."""

import shutil
import subprocess
import sys
from pathlib import Path

from PyQt5 import QtWidgets, uic

from crisprmatch.resources import ui_path


UiMergeDialog, _ = uic.loadUiType(ui_path("flash_merge.ui"))


class MergeDialog(QtWidgets.QDialog, UiMergeDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Merge FASTQ")
        self.left_fastq = None
        self.right_fastq = None
        self.output_dir = None

        self.left.setReadOnly(True)
        self.right.setReadOnly(True)
        self.output.setReadOnly(True)
        self.leftbtn.clicked.connect(lambda: self.select_fastq("left"))
        self.rightbtn.clicked.connect(lambda: self.select_fastq("right"))
        self.outputbtn.clicked.connect(self.select_output)
        self.pushButton.clicked.connect(self.merge)

    def select_fastq(self, side):
        selected, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open FASTQ file",
            str(Path.cwd()),
            "FASTQ files (*.fastq *.fq *.fastq.gz *.fq.gz);;All files (*)",
        )
        if not selected:
            return
        if side == "left":
            self.left_fastq = selected
            self.left.setText(selected)
        else:
            self.right_fastq = selected
            self.right.setText(selected)

    def select_output(self):
        selected = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select output directory", str(Path.cwd())
        )
        if selected:
            self.output_dir = selected
            self.output.setText(selected)

    def merge(self):
        output_name = self.name.text().strip()
        if not output_name or not self.left_fastq or not self.right_fastq or not self.output_dir:
            QtWidgets.QMessageBox.warning(
                self,
                "Missing input",
                "Select both FASTQ files, an output directory, and an output name.",
            )
            return

        flash = shutil.which("flash")
        if not flash:
            QtWidgets.QMessageBox.warning(
                self,
                "FLASH not found",
                "Activate the CRISPRMatch conda environment and try again.",
            )
            return

        output_dir = Path(self.output_dir)
        command = [
            flash,
            "-o",
            output_name,
            "-t",
            str(self.spinBox.value()),
            "-d",
            str(output_dir),
            self.left_fastq,
            self.right_fastq,
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        log_path = output_dir / f"{output_name}_flash.log"
        log_path.write_text(completed.stdout + completed.stderr, encoding="utf-8")
        if completed.returncode:
            QtWidgets.QMessageBox.critical(
                self,
                "FLASH failed",
                f"FLASH exited with code {completed.returncode}. See {log_path}",
            )
            return

        QtWidgets.QMessageBox.information(
            self,
            "Finished",
            f"Merged reads are in {output_dir / (output_name + '.extendedFrags.fastq')}",
        )


# Compatibility with code that imported the old class name.
showtable = MergeDialog


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = MergeDialog()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
