#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020, Borting Chen <bortingchen@gmail.com>
#
# This file is licensed under the GPL v2.
#

import sys

from enum import IntEnum
from PyQt5.QtWidgets import *
from PyQt5 import uic
from pathlib import Path

from core import *

class GodMainWin(QMainWindow):
    def __init__(self, parent=None):
        super(GodMainWin, self).__init__(parent)

        # Load ui file
        uic.loadUi(str(Path(__file__).parents[0]/"window.ui"), self)

        # Adjust height if a global menubar is used
        if self.menuBar.isNativeMenuBar():
            self.setMaximumHeight(self.height() - self.menuBar.height())

        # Set default value
        self._previewCmd = "/usr/bin/meld"
        self._oldDirName = "old"
        self._newDirName = "new"

        # Connect signals and slots
        self.gitRepoBtn.clicked.connect(self._getGitRepoDir)
        self.outDirBtn.clicked.connect(self._getOutDir)
        self.previewBtn.clicked.connect(self._preview)
        self.generateBtn.clicked.connect(lambda: self._generate(preview=False))
        self.aboutAction.triggered.connect(self._actAbout)

    def _actAbout(self, checked):
        aboutStr = """
        <center>
        <h4>Generate Old-style Diff</h4>
        <p>v2.0</p>
        <p><a href="https://github.com/borting/gen-old-diff">GOD GitHub</a></p>
        <p>Copyright \N{COPYRIGHT SIGN} 2020 Borting Chen</p>
        """
        QMessageBox.about(self, "About GOD", aboutStr)

    def _getGitRepoDir(self):
        gitRepoDig = QFileDialog()
        gitRepoDig.setFileMode(QFileDialog.Directory)

        gitRepoDir = self.gitRepoEdit.text()
        if not gitRepoDir or not Path(gitRepoDir).exists():
            gitRepoDir = str(Path())

        gitRepoDir = gitRepoDig.getExistingDirectory(self, self.tr("Open Git Repository"), 
                gitRepoDir, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)

        # Update gitRepoEdit if user chooses a dir
        if gitRepoDir:
            self.gitRepoEdit.setText(gitRepoDir)

    def _getOutDir(self):
        outDig = QFileDialog()
        outDig.setFileMode(QFileDialog.Directory)

        outDir = self.outDirEdit.text()
        if not outDir or not Path(outDir).exists() or not Path(outDir).is_dir():
            outDir = str(Path())

        outDir = outDig.getExistingDirectory(self, self.tr("Open Output Directory"), 
                outDir, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)

        # Update outDirEdit if user chooses a dir
        if outDir:
            self.outDirEdit.setText(outDir)


    def _checkLineEdit(self, preview=False):
        warnStr = ""

        if not self.gitRepoEdit.text():
            warnStr += '"Git Repository", '

        if not self.newCmtEdit.text():
            warnStr += '"Modified Commit", '

        if (preview == False):
            if not self.outDirEdit.text():
                warnStr += '"Output Directory", '

            if self.outFileExtCombo.currentText() and not self.outFileEdit.text():
                warnStr += '"Output Filename", '

        if warnStr:
            warnStr = warnStr[:-2] + " cannot be empty."
            QMessageBox.critical(self, "Error", warnStr)

        return warnStr


    def _preview(self):
        if self._checkLineEdit(preview=True):
            return

        try:
            if self.oldCmtEdit.text():
                g = GOD(self.gitRepoEdit.text(), self.newCmtEdit.text(), self.oldCmtEdit.text())
            else:
                g = GOD(self.gitRepoEdit.text(), self.newCmtEdit.text())

            action = genPreviewAction([self._previewCmd])
            g.generate(action)

        except GitRepoException as err:
            QMessageBox.critical(self, "Error", err)
        except CommitIdException as err:
            QMessageBox.critical(self, "Error", err)

    def _generate(self, preview):
        # Check LineEdit are not empty according to selection
        if self._checkLineEdit(preview):
            return

        try:
            if self.oldCmtEdit.text():
                g = GOD(self.gitRepoEdit.text(), self.newCmtEdit.text(), self.oldCmtEdit.text() + "^")
            else:
                g = GOD(self.gitRepoEdit.text(), self.newCmtEdit.text(), self.newCmtEdit.text() + "^")

            if not preview:
                ext = self.outFileExtCombo.currentText()
                if ext:
                    outFile = Path(self.outDirEdit.text() + "/" + self.outFileEdit.text() + ext)
                    outFile.touch(exist_ok=False)
                else:
                    outFile = Path(self.outDirEdit.text() + "/" + self.outFileEdit.text())
                    outFile.mkdir(parents=False, exist_ok=False)

                if (ext == ".tar.gz") or (ext == ".tgz"):
                    action = genTarCompress(outFile, "w:gz")
                elif (ext == ".tar.xz") or (ext == ".txz"):
                    action = genTarCompress(outFile, "w:xz")
                elif (ext == ".actiontar.bz2") or (ext == ".tbz2"):
                    action = genTarCompress(outFile, "w:bz2")
                elif (ext == ".zip"):
                    action = genZipCompress(outFile)
                else:
                    action = genDiffDirs(outFile)

            g.generate(action)

            QMessageBox.information(self, "Success", "'{}' has been generated.".format(str(outFile)))

        except GitRepoException as err:
            QMessageBox.critical(self, "Error", err)
        except CommitIdException as err:
            QMessageBox.critical(self, "Error", err)
        except FileExistsError as err:
            QMessageBox.critical(self, "Error", "File already exists: '{}'.".format(err.filename))
        except FileNotFoundError as err:
            QMessageBox.critical(self, "Error", "No such directory '()'.".format(Path(err.filename).parents[0]))

def main():
    app = QApplication(sys.argv)
    gui = GodMainWin()
    gui.show()
    sys.exit(app.exec_())

if __name__=="__main__":
    main()

