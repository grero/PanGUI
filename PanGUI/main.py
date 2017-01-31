import sys
from PyQt4 import QtCore, QtGui
from PyQt4.uic import loadUiType
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

Ui_MainWindow, QMainWindow = loadUiType("GUI.ui")

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, plotobject):
        """

        :type plotobject: object
        """
        super(Main, self).__init__()
        self.setupUi(self)
        self.prevButton.clicked.connect(self.goprev)
        self.nextButton.clicked.connect(self.gonext)
        self.index = 0
        self.plotobject = plotobject
        self.currentIndex.setText(str(self.index))
        fig1 = Figure()
        fig1.set_facecolor((0.92, 0.92, 0.92))
        fig1.set_tight_layout(True)
        ax1f1 = fig1.add_subplot(111)
        ax1f1.spines["top"].set_visible(False)
        ax1f1.spines["right"].set_visible(False)
        ax1f1.xaxis.set_ticks_position("bottom")
        ax1f1.yaxis.set_ticks_position("left")
        self.addmpl(fig1)
        plotobject.plot(self.index,ax=self.fig.axes[0])
        self.setWindowTitle(plotobject.title)


    def addmpl(self, fig):
        self.fig = fig
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,
                                         self.mplwindow,
                                         coordinates=True)
        self.toolbar.hide()
        self.mplvl.addWidget(self.toolbar)
        self.actionZoom.triggered.connect(self.toolbar.zoom)
        self.actionReset_Zoom.triggered.connect(self.toolbar.home)
        self.actionPan.triggered.connect(self.toolbar.pan)

    def gonext(self):
        self.fig.axes[0].cla()
        self.index = min(self.plotobject.data.shape[0]-1, self.index+1)
        self.plotobject.plot(self.index, ax=self.fig.axes[0])
        self.canvas.draw()
        self.currentIndex.setText(str(self.index))

    def goprev(self):
        self.fig.axes[0].cla()
        self.index = max(0, self.index-1)
        self.plotobject.plot(self.index, ax=self.fig.axes[0])
        self.canvas.draw()
        self.currentIndex.setText(str(self.index))


def create_window(window_class,args):
    """
    Create a new window based on `window_class`. This works whether called from IPython terminal or as a script
    Based on: http://cyrille.rossant.net/making-pyqt4-pyside-and-ipython-work-together/
    :param window_class:
    :return window:
    """
    app_created = False
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
        app_created = True
    app.references = set()
    window = window_class(args)
    app.references.add(window)
    window.show()
    if app_created:
        app.exec_()
    return window
