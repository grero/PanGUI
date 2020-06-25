import sys
import os
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUiType
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

guipath = __file__.split(os.sep)
guipath[-1] = "GUI.ui"
guifile = os.sep.join(guipath)
Ui_MainWindow, QMainWindow = loadUiType(guifile)


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, plotobjs, rows=None, cols=None, indexer=None):
        """

        :type plotobject: object
        """
        super(Main, self).__init__()
        self.setupUi(self)
        self.prevButton.clicked.connect(self.goprev)
        self.nextButton.clicked.connect(self.gonext)
        self.currentIndex.editingFinished.connect(self.updateIndex)
        self.index = 0
        # hack to allow singleton argument here
        if hasattr(plotobjs, '__getitem__'):
            self.plotobjs = plotobjs
        else:
            self.plotobjs = [plotobjs]
        self.currentIndex.setText(str(self.index))
        fig1 = Figure()
        fig1.set_facecolor((0.92, 0.92, 0.92))
        self.addmpl(fig1)
        if cols is None:
            cols = 1
        if rows is None:
            rows = np.ceil(len(self.plotobjs)/cols)

        self.indexer = indexer
        self.indexers = [plotobj.getindex(self.indexer) for plotobj
                         in self.plotobjs]

        for (i, plotobj) in enumerate(self.plotobjs):
            ax = fig1.add_subplot(rows, cols, i+1)
            plotobj.plot(self.indexers[i](self.index), ax)

        self.active_plotobj = None

    def addmpl(self, fig):
        self.fig = fig
        self.canvas = FigureCanvas(fig)
        self.toolbar = NavigationToolbar(self.canvas,
                                         self.mplwindow,
                                         coordinates=True)
        self.toolbar.show()
        self.mplvl.addWidget(self.toolbar)
        self.actionZoom.triggered.connect(self.toolbar.zoom)
        self.actionReset_Zoom.triggered.connect(self.toolbar.home)
        self.actionPan.triggered.connect(self.toolbar.pan)
        self.mplvl.addWidget(self.canvas)
        self.canvas.mpl_connect("button_press_event", self.onclick)
        self.canvas.draw()

    def onclick(self, event):
        if event.button == 3:  # right button
            if event.inaxes is not None:
                # figure out what is being plotted
                axidx = self.fig.axes.index(event.inaxes)
                plotobj = self.plotobjs[axidx]
                self.active_plotobj = plotobj
                popupMenu = QtWidgets.QMenu(self)
                for (k,v) in plotobj.plotopts.items():
                    if isinstance(v, bool):
                        action = QtWidgets.QAction(k, self)
                        action.setCheckable(True)
                        action.setChecked(v)
                        popupMenu.addAction(action)
                cursor = QtGui.QCursor()
                popupMenu.triggered[QtWidgets.QAction].connect(self.setplotopts)
                popupMenu.popup(cursor.pos())

    def setplotopts(self, q):
        if self.active_plotobj is not None:
            self.active_plotobj.plotopts[q.text()] = q.isChecked()
            print(self.active_plotobj.plotopts[q.text()])

    def update_index(self, new_index):
        index = self.index
        for indexer in self.indexers:
            if len(indexer(new_index)) > 0:
                index = new_index
            else:
                index = self.index

        self.index = index

    def gonext(self):
        self.update_index(self.index+1)
        self.currentIndex.setText(str(self.index))
        for (i, plotobj) in enumerate(self.plotobjs):
            plotobj.plot(self.indexers[i](self.index), self.fig.axes[i])
        self.canvas.draw()
        # I don't think should be necessary here, but the plot doesn't
        # seem to update otherwise
        self.repaint()

    def goprev(self):
        self.update_index(self.index-1)
        self.currentIndex.setText(str(self.index))
        for (i, plotobj) in enumerate(self.plotobjs):
            plotobj.plot(self.indexers[i](self.index), self.fig.axes[i])
        self.canvas.draw()
        self.repaint()

    def updateIndex(self):
        self.update_index(int(self.currentIndex.text()))
        self.currentIndex.setText(str(self.index))  # Update the index shown
        for (i, plotobj) in enumerate(self.plotobjs):
            plotobj.plot(self.indexers[i](self.index), self.fig.axes[i])
        self.canvas.draw()


def create_window(plotobj,  window_class=Main, **kwargs):
    """
    Create a new window based on `window_class`. This works whether called from IPython terminal or as a script
    Based on: http://cyrille.rossant.net/making-pyqt4-pyside-and-ipython-work-together/
    :param window_class:
    :return window:
    """
    app_created = False
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        app_created = True
    app.references = set()
    window = window_class(plotobj, **kwargs)
    app.references.add(window)
    window.show()
    if app_created:
        app.exec_()
    return window
