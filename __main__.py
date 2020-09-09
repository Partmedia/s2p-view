#!/usr/bin/env python3
"""
Copyright (c) 2018 Kevin Zheng

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
import skrf as rf

from about import Ui_About
from layout import Ui_MainWindow

class AboutDialog(QDialog, Ui_About):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, path):
        super().__init__()
        self.fig = Figure()
        self.setupUi(self)
        self.about = AboutDialog()
        self.open(path)

        self.actionAbout.triggered.connect(lambda: self.about.show())
        self.action_Open.triggered.connect(self.openDialog)
        self.enableSmith(self.comboDisplay.currentText())
        self.comboDisplay.currentTextChanged.connect(self.enableSmith)
        self.plotButton.pressed.connect(self.plot)
        self.show()

    def openDialog(self):
        path, _ = QFileDialog.getOpenFileName(self,
                filter="S-Parameter Files (*.s?p)")
        if len(path) > 0:
            self.open(path)

    def open(self, path):
        self.net = rf.Network(path)
        dim = self.net.s.shape[1]
        def checkEnable(checkbox, ndims):
            if ndims <= dim:
                checkbox.setEnabled(True)
                checkbox.setChecked(True)
            else:
                checkbox.setEnabled(False)
        checkEnable(self.checkS11, 1)
        checkEnable(self.checkS21, 2)
        checkEnable(self.checkS12, 2)
        checkEnable(self.checkS22, 2)
        self.plot()

    def plot(self):
        self.net.frequency.unit = self.comboUnit.currentText().lower()
        data = self.net
        r = self.lineRange.text()
        if len(r) > 0:
            try:
                data = data[r]
            except (ValueError, KeyError):
                self.statusbar.showMessage("Invalid range!", 3000)
                return

        self.statusbar.showMessage("Plotting...", 1000)
        self.fig.clear()
        self.ax = self.fig.subplots()
        s = self.comboDisplay.currentText()
        plot_fn = None
        if s == 'Magnitude':
            plot_fn = lambda x, m, n: x.plot_s_db(m=m, n=n, ax=self.ax)
        elif s == 'Phase':
            plot_fn = lambda x, m, n: x.plot_s_deg(m=m, n=n, ax=self.ax)
        elif s == 'Smith':
            plot_fn = lambda x, m, n: x.plot_s_smith(m=m, n=n, ax=self.ax,
                    draw_labels=self.checkLabels.isChecked(),
                    draw_vswr=self.checkVSWR.isChecked())

        def plotIfChecked(c, m, n):
            if c.isChecked():
                plot_fn(data, m, n)

        plotIfChecked(self.checkS11, 0, 0)
        plotIfChecked(self.checkS21, 1, 0)
        plotIfChecked(self.checkS12, 0, 1)
        plotIfChecked(self.checkS22, 1, 1)
        self.canvas.draw()
        self.canvas.flush_events()

    def enableSmith(self, t):
        self.comboUnit.setEnabled(t != 'Smith')
        self.smithBox.setEnabled(t == 'Smith')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: s2p-view FILE", file=sys.stderr)
        sys.exit(1)
    app = QApplication([])
    window = MainWindow(sys.argv[1])
    app.exec_()
