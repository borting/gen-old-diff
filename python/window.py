#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020, Borting Chen <bortingchen@gmail.com>
#
# This file is licensed under the GPL v2.
#

from enum import IntEnum
from PyQt5.QtWidgets import *
from PyQt5 import uic
from pathlib import Path

import sys
from core import *

class GodMainWin(QMainWindow):
    def __init__(self, parent=None):
        super(GodMainWin, self).__init__(parent)

        # Load ui file
        uic.loadUi(str(Path(__file__).parents[0]/"window.ui"), self)

        # Disable preview
        self.previewBtn.setEnabled(False)

        # Adjust height if a global menubar is used
        if self.menuBar.isNativeMenuBar():
            self.setMaximumHeight(self.height() - self.menuBar.height())

        # Connect signals and slots
        self.gitRepoBtn.clicked.connect(self.getGitRepoDir)
        self.outDirBtn.clicked.connect(self.getOutDir)
        self.previewBtn.clicked.connect(lambda: self._generate(preview=True))
        self.generateBtn.clicked.connect(lambda: self._generate(preview=False))

    def getGitRepoDir(self):
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

    def getOutDir(self):
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

    def _generate(self, preview):
        # Check LineEdit are not empty according to selection
        if self._checkLineEdit(preview):
            return

        try:
            if self.oldCmtEdit.text():
                g = GOD(self.gitRepoEdit.text(), self.newCmtEdit.text(), self.oldCmtEdit.text())
            else:
                g = GOD(self.gitRepoEdit.text(), self.newCmtEdit.text())

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

