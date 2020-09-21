#!/usr/bin/env python3
"""
Copyright (c) 2018, 2020 Kevin Zheng

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
    def __init__(self, paths):
        super().__init__()
        self.fig = Figure()
        self.setupUi(self)
        self.about = AboutDialog()

        self.networks = []      # list of currently open rf.Network
        self.network_dims = []  # max dimension of currently open networks

        self.openMany(paths)

        self.actionAbout.triggered.connect(lambda: self.about.show())
        self.action_Open.triggered.connect(self.openDialog)
        self.actionSave_Plot.triggered.connect(self.savePlot)
        self.actionClose_All.triggered.connect(self.closeAll)
        self.enableSmith(self.comboDisplay.currentText())
        self.comboDisplay.currentTextChanged.connect(self.enableSmith)
        self.plotButton.pressed.connect(self.plot)
        self.show()

    def openDialog(self):
        paths, _ = QFileDialog.getOpenFileNames(self,
                filter="S-Parameter Files (*.s?p)")
        if len(paths) > 0:
            self.openMany(paths)

    def savePlot(self):
        path, _ = QFileDialog.getSaveFileName(self, filter="Plot Outputs (*.eps, *.pdf, *.pgf, *.png, *.ps, *.raw, *.rgba, *.svg, *.svgz)")
        if len(path) > 0:
            try:
                self.fig.savefig(path)
            except Exception as e:
                QMessageBox.critical(self, "Save Plot Error", str(e))

    def closeAll(self):
        self.networks = []
        self.network_dims = []
        self.refreshNets()

    def checkDimEnable(self):
        """
        Enable/disable port plot checkboxes based on maximum currently-loaded
        dimension.
        """
        dim = max(self.network_dims + [0])  # handle empty network_dims
        def checkEnable(checkbox, ndims):
            if ndims <= dim:
                checkbox.setEnabled(True)
                checkbox.setChecked(True)
            else:
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
        checkEnable(self.checkS11, 1)
        checkEnable(self.checkS21, 2)
        checkEnable(self.checkS12, 2)
        checkEnable(self.checkS22, 2)

    def open(self, path):
        net = rf.Network(path)
        dim = net.s.shape[1]
        self.networks.append(net)
        self.network_dims.append(dim)

    def refreshNets(self):
        self.checkDimEnable()
        self.plot()

    def openMany(self, paths):
        for path in paths:
            self.open(path)
        self.refreshNets()

    def plot(self):
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
        elif s == 'Z Real':
            plot_fn = lambda x, m, n: x.plot_z_re(m=m, n=n, ax=self.ax)
        elif s == 'Z Imag':
            plot_fn = lambda x, m, n: x.plot_z_im(m=m, n=n, ax=self.ax)

        for data, dim in zip(self.networks, self.network_dims):
            data.frequency.unit = self.comboUnit.currentText().lower()
            r = self.lineRange.text()
            if len(r) > 0:
                try:
                    data = data[r]
                except (ValueError, KeyError):
                    self.statusbar.showMessage("Invalid range!", 3000)
                    return

            def plotIfChecked(c, m, n):
                if c.isChecked() and m < dim and n < dim:
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
    app = QApplication([])
    window = MainWindow(sys.argv[1:])
    app.exec_()
