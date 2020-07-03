import sys
import os
import numpy as np
import DataProcessingTools as DPT
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
    def __init__(self, plotobjs, rows=None, cols=None, indexer=None,
                 linkxaxes=None, linkyaxes=None):
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

        _levels = []
        for obj in self.plotobjs:
            for l in obj.getlevels():
                if l not in _levels:
                    _levels.append(l)

        self.levelSelection.addItems(_levels)
        self.levelSelection.currentIndexChanged.connect(self.update_level)

        self.currentIndex.setText(str(self.index))
        fig1 = Figure()
        fig1.set_facecolor((0.92, 0.92, 0.92))
        self.addmpl(fig1)
        if cols is None:
            cols = 1
        if rows is None:
            rows = np.ceil(len(self.plotobjs)/cols)

        if linkxaxes is None:
            linkxaxes = range(len(self.plotobjs))
        if linkyaxes is None:
            linkyaxes = range(len(self.plotobjs))

        for (i, plotobj) in enumerate(self.plotobjs):
            if linkxaxes[i] < i:
                sharex = fig1.axes[linkxaxes[i]]
            else:
                sharex = None
            if linkyaxes[i] < i:
                sharey = fig1.axes[linkxaxes[i]]
            else:
                sharey = None
            ax = fig1.add_subplot(rows, cols, i+1, sharex=sharex,
                                  sharey=sharey)
            plotobj.plot(self.index, ax)

        self.active_plotobj = None
        self.levelSelection.setCurrentIndex(_levels.index(self.plotobjs[0].level))

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

    def update_level(self, lidx):
        level = self.levelSelection.currentText()
        for obj in self.plotobjs:
            obj.update_index(level)
        # make sure the old index is still valid
        self.currentIndex.setText("0")
        self.updateIndex()

    def onclick(self, event):
        if event.button == 3:  # right button
            if event.inaxes is not None:
                # figure out what is being plotted
                axidx = self.fig.axes.index(event.inaxes)
                plotobj = self.plotobjs[axidx]
                self.active_plotobj = plotobj
                popupMenu = QtWidgets.QMenu(self)
                self.create_menu(plotobj.plotopts, popupMenu)
                cursor = QtGui.QCursor()
                popupMenu.triggered[QtWidgets.QAction].connect(self.setplotopts)
                popupMenu.popup(cursor.pos())

    def create_menu(self, q, menu=None, cpath=""):
        if menu is None:
            popupMenu = QtWidgets.QMenu(self)
        else:
            popupMenu = menu

        for (k, v) in q.items():
            if isinstance(v, bool):
                action = QtWidgets.QAction(k, self)
                action.setCheckable(True)
                action.setChecked(v)
                action.setData({"path": "_".join((cpath, menu.title()))})
                menu.addAction(action)
            elif isinstance(v, dict):
                if cpath != "":
                    qpath = "_".join((cpath, k))
                else:
                    qpath = k
                subMenu = menu.addMenu(k)
                self.create_menu(v, subMenu, qpath)
            elif isinstance(v, DPT.objects.ExclusiveOptions):
                subMenu = menu.addMenu(k)
                ag = QtWidgets.QActionGroup(self, exclusive=True)
                for (ii, oo) in enumerate(v.options):
                    action = ag.addAction(QtWidgets.QAction(oo, self, checkable=True))
                    if cpath != "":
                        qpath = "_".join((cpath, subMenu.title()))
                    else:
                        qpath = subMenu.title()
                    action.setData({"path": qpath, "key": k})
                    if v.checked == ii:
                        action.setChecked(True)
                    else:
                        action.setChecked(False)
                    subMenu.addAction(action)
            else:
                action = QtWidgets.QAction(k, self)
                action.setData({"value": v, "path": cpath})
                menu.addAction(action)

    def setplotopts(self, q):
        if self.active_plotobj is not None:
            idx = self.plotobjs.index(self.active_plotobj)

            # unwind path
            plotopts = {}
            qpath = q.data()["path"]
            _opts = plotopts
            if qpath:
                cpath = qpath.split("_")
                for k in cpath:
                   aa = {}
                   _opts[k] = aa
                   _opts = _opts[k]

            if q.isCheckable():
                _opts[q.text()] = q.isChecked()

            elif not q.isCheckable() and q.menu() is None:  # Text input
                text, okPressed = QtWidgets.QInputDialog.getText(self,q.text(),"",
                                                                 QtWidgets.QLineEdit.Normal,
                                                                 str(q.data()["value"]))
                if okPressed:
                    # unwind the path
                    _opts[q.text()] = type(q.data()["value"])(text)

            self.active_plotobj.update_plotopts(plotopts, self.fig.axes[idx])
            self.canvas.draw()
            self.repaint()

    def update_index(self, new_index):
        index = self.index
        for plotobj in self.plotobjs:
            if len(plotobj.indexer(new_index)) > 0:
                index = new_index
            else:
                index = self.index

        self.index = index

    def gonext(self):
        self.update_index(self.index+1)
        self.currentIndex.setText(str(self.index))
        for (i, plotobj) in enumerate(self.plotobjs):
            plotobj.plot(self.index, self.fig.axes[i])
        self.canvas.draw()
        # I don't think should be necessary here, but the plot doesn't
        # seem to update otherwise
        self.repaint()

    def goprev(self):
        self.update_index(self.index-1)
        self.currentIndex.setText(str(self.index))
        for (i, plotobj) in enumerate(self.plotobjs):
            plotobj.plot(self.index, self.fig.axes[i])
        self.canvas.draw()
        self.repaint()

    def updateIndex(self):
        self.update_index(int(self.currentIndex.text()))
        self.currentIndex.setText(str(self.index))  # Update the index shown
        for (i, plotobj) in enumerate(self.plotobjs):
            plotobj.plot(self.index, self.fig.axes[i])
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
