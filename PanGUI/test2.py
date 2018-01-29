import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from PyQt5.uic import loadUiType
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

import glob
import h5py

picked_lines = []


class SimplerToolbar(NavigationToolbar):
    toolitems = [t for t in NavigationToolbar.toolitems if
                    t[0] in ("Home", "Pan", "Zoom")]

    def __init__(self, *args, **kwargs):
        super(SimplerToolbar, self).__init__(*args, **kwargs)


class ViewWidget(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        layout = QVBoxLayout()
        self.mainWidget.setLayout(layout)

        self.figure_canvas = FigureCanvas(Figure())
        self.navigation_toolbar = SimplerToolbar(self.figure_canvas, self)
        layout.addWidget(self.navigation_toolbar, 0)
        layout.addWidget(self.figure_canvas, 10)
        self.figure = self.figure_canvas.figure
        self.figure.canvas.mpl_connect('pick_event', self.pick_event)
        ax = self.figure.add_subplot(111)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xlabel("State")
        ax.set_ylabel("Amplitude")

        self.picked_lines = []

    def pick_event(self, event):
        artist = event.artist
        lw = artist.get_linewidth()
        label = artist.get_label()
        if lw == 1.5:
            artist.set_linewidth(2*lw)
            self.picked_lines.append(label)
        elif lw > 1.5:
            artist.set_linewidth(lw/2)
            self.picked_lines.remove(label)
        artist.figure.canvas.draw()

    def plot_waveforms(self, waveforms, pp):
        ax = self.figure.axes[0]
        for i in xrange(waveforms.shape[0]):
            ax.plot(waveforms[i, 0, :], label="Waveform %d" % (i, ), picker=5)
        ax.legend()

    def select_waveforms(self, fname="spike_templates.hdf5"):
        files = glob.glob(fname)
        if files:
            for f in files:
                with h5py.File(f, "r") as ff:
                    waveforms = ff["spikeForms"][:]
                    pp = ff["p"][:]
                    self.plot_waveforms(waveforms, pp)

def plot_waveforms(waveforms, pp):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlabel("State")
    ax.set_ylabel("Amplitude")
    for i in xrange(waveforms.shape[0]):
        ax.plot(waveforms[i, 0, :], label="Waveform %d" % (i, ), picker=5)
    plt.legend()
    fig.canvas.mpl_connect('pick_event', pick_event)


def pick_event(event):
    artist = event.artist
    lw = artist.get_linewidth()
    label = artist.get_label()
    if lw == 1.5:
        artist.set_linewidth(2*lw)
        picked_lines.append(label)
    elif lw > 1.5:
        artist.set_linewidth(lw/2)
        picked_lines.remove(label)
    artist.figure.canvas.draw()


def select_waveforms(fname="spike_templates.hdf5"):
        files = glob.glob(fname)
        if files:
            for f in files:
                with h5py.File(f, "r") as ff:
                    waveforms = ff["spikeForms"][:]
                    print waveforms.shape
                    pp = ff["p"][:]
                    plot_waveforms(waveforms, pp)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = ViewWidget()
    mw.select_waveforms()
    mw.show()
    sys.exit(app.exec_())
