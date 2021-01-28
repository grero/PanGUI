import sys
import os
import copy
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
                 linkxaxes=None, linkyaxes=None, **kwargs):
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
        self.plotopts = [plotobj.plot(getPlotOpts=True) for plotobj in self.plotobjs]
        for plotopts in self.plotopts:
            for (k, v) in kwargs.items():
                if k in plotopts.keys():
                    if isinstance(plotopts[k], DPT.objects.ExclusiveOptions):
                        plotopts[k].select(v)
                    else:
                        plotopts[k] = v

        self.currentIndex.setText(str(self.index))
        fig1 = Figure()
        fig1.set_facecolor((0.92, 0.92, 0.92))
        self.addmpl(fig1)
        if cols is None:
            cols = 1
        if rows is None:
            rows = int(np.ceil(len(self.plotobjs)/cols))

        if linkxaxes is None:
            linkxaxes = range(len(self.plotobjs))
        if linkyaxes is None:
            linkyaxes = range(len(self.plotobjs))

        self.linkxaxes = linkxaxes
        self.linkyaxes = linkyaxes
        self.numEvents = 100000
        for (i, plotobj) in enumerate(self.plotobjs):
            ax = fig1.add_subplot(rows, cols, i+1)
        
            nn, newIdx = plotobj.plot(self.index, getNumEvents=True)
            self.numEvents = min(self.numEvents, nn)
            plotobj.plot(self.index, ax=ax, **self.plotopts[i])
            if newIdx is not None and newIdx != self.index:
                self.currentIndex.setText(str(newIdx))
                self.updateIndex()

        # set up axes sharing
        for (i, plotobj) in enumerate(self.plotobjs):
            ax = fig1.axes[i]
            if linkxaxes[i] != i:
                sharex = fig1.axes[linkxaxes[i]]
            else:
                sharex = None
            if linkyaxes[i] != i:
                sharey = fig1.axes[linkyaxes[i]]
            else:
                sharey = None

            # explicitly update the x- and y-axis limits
            if sharex is not None:
                ax.set_xlim(sharex.get_xlim())
                ax.sharex(sharex)
            if sharey is not None:
                ax.set_ylim(sharey.get_ylim())
                ax.sharey(sharey)

        self.active_plotobj = None
        self.active_axis = None
        self.active_obj_idx = 0

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
                if axidx < len(self.plotobjs):
                    plotobj = self.plotobjs[axidx]
                    self.active_obj_idx  = axidx
                else:
                    # e.g. ax is the result of twinx
                    # attempt to use axis position to figure out the index
                    pos0 = event.inaxes.get_position()
                    for (ii, _ax) in enumerate(self.fig.axes):
                        pos1 = _ax.get_position()
                        if np.allclose(pos0, pos1):
                            plotobj = self.plotobjs[ii]
                            self.active_obj_idx = ii
                            break

                self.active_plotobj = plotobj
                plotopts = self.plotopts[self.active_obj_idx]
                popupMenu = QtWidgets.QMenu(self)
                self.create_menu(plotopts, popupMenu)
                self.active_axis = event.inaxes

                # add popup dialog as the last optoon
                daction = QtWidgets.QAction("Set all...", self)
                popupMenu.addAction(daction)

                cursor = QtGui.QCursor()
                popupMenu.triggered[QtWidgets.QAction].connect(self.setplotopts)
                daction.triggered.connect(self.create_dialog)
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

                if cpath:
                    qpath = "_".join((cpath, menu.title()))
                else:
                    qpath = menu.title()
                action.setData({"path": qpath})
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
        # Kind of hackish, but needed since setplotopts currently gets called for any
        # menu selection
        if len(self.plotobjs) > 1:
            replotAll = False
        else:
            replotAll = True
        if q.text() == "Set all...":
            return None
        if self.active_plotobj is not None:
            # TODO: Do we really need to do this?

            idx = self.active_obj_idx

            plotopts = self.plotopts[idx]

            # unwind path
            qpath = q.data()["path"]
            _opts = plotopts
            _popts = self.preOpts[idx]
            if qpath:
                cpath = qpath.split("_")
                for k in cpath:
                    _opts = _opts[k]
                    _popts = _popts[k]

            if isinstance(_opts, DPT.objects.ExclusiveOptions):
                if q.isChecked():
                    _popts.select(_opts.selected)
                    _opts.select(q.text())
            elif q.isCheckable():
                _popts[q.text()] = _opts[q.text()]
                _opts[q.text()] = q.isChecked()
            elif not q.isCheckable() and q.menu() is None:  # Text input
                text, okPressed = QtWidgets.QInputDialog.getText(self,q.text(),"",
                                                                 QtWidgets.QLineEdit.Normal,
                                                                 str(q.data()["value"]))
                if okPressed:
                    # unwind the path
                    _popts[q.text()] = _opts[q.text()]
                    _opts[q.text()] = type(q.data()["value"])(text)

            if replotAll:
                # update all objects with the new level info
                self.update_level(q.text())
                for ii in range(len(self.plotobjs)):
                    if ii != idx:
                        self.plotobjs[ii].plot(self.index, ax=self.fig.axes[ii], **self.plotopts[ii])

            numEvents, nidx = self.active_plotobj.plot(self.index, getNumEvents=True, **self.plotopts[idx])
            if numEvents != self.numEvents:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText("""Warning: The selected object reports {0} event(s), while the current number of events is {1}.
                        """.format(numEvents, self.numEvents))
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                retval = msg.exec_()
            self.active_plotobj.plot(self.index, ax=self.fig.axes[idx], **self.plotopts[idx])

            self.canvas.draw()
            self.repaint()

    def create_dialog(self, q, plotopts=None, dialog=None):
        """
        Dynamically create a dialog based on the contentents
        of the dictionary `plotopts`.
        """
        if dialog is None:
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Set plot options")
            layout = QtWidgets.QVBoxLayout()
            dialog.setLayout(layout)
            tabs = QtWidgets.QTabWidget(dialog)
            layout.addWidget(tabs)
            plotopts = [copy.deepcopy(plotopt) for plotopt in self.plotopts]
            for (ii, plotopt) in enumerate(plotopts):
                tab = QtWidgets.QWidget()
                tabs.addTab(tab, "Obj {0}".format(ii))
                tlayout = QtWidgets.QVBoxLayout()
                tab.setLayout(tlayout)
                self.create_dialog(q, plotopt, tlayout)
            blayout = QtWidgets.QHBoxLayout()
            buttonOK = QtWidgets.QPushButton("OK")
            blayout.addWidget(buttonOK)
            buttonOK.clicked.connect(dialog.accept)
            buttonCancel = QtWidgets.QPushButton("Cancel")
            blayout.addWidget(buttonCancel)
            layout.addLayout(blayout)

            buttonCancel.clicked.connect(dialog.reject)
            dialog.setModal(True)
            result = dialog.exec_()
            if result:
                #TODO: Make this work for twinx as well
                self.plotopts = plotopts
                self.update_level("test")
                for (ax, plotobj, plotopt) in zip(self.fig.axes, self.plotobjs, self.plotopts):
                    plotobj.plot(self.index, ax=ax, **plotopt)
                self.canvas.draw()
                self.repaint()
        else:
            for (k, v) in plotopts.items():
                if isinstance(v, dict):
                    group = QtWidgets.QGroupBox(k)
                    layout = QtWidgets.QVBoxLayout(group)
                    dialog.addWidget(group)
                    self.create_dialog(q, v, layout)
                elif isinstance(v, bool):
                    aa = QtWidgets.QCheckBox(k)
                    dialog.addWidget(aa)
                    aa.setChecked(v)
                    aa.stateChanged.connect(lambda state, k=k: plotopts.__setitem__(k, state == QtCore.Qt.Checked))
                elif isinstance(v, DPT.objects.ExclusiveOptions):
                    layout = QtWidgets.QVBoxLayout()
                    for (ii, oo) in enumerate(v.options):
                        rr = QtWidgets.QRadioButton(oo)
                        if ii == v.checked:
                            rr.setChecked(True)
                        else:
                            rr.setChecked(False)

                        rr.toggled.connect(lambda state, oo=oo, v=v: state and v.select(oo))


                        layout.addWidget(rr)
                    group = QtWidgets.QGroupBox(k)
                    group.setLayout(layout)
                    dialog.addWidget(group)
                else:
                    layout = QtWidgets.QHBoxLayout()
                    label = QtWidgets.QLabel(k)
                    layout.addWidget(label)
                    aa = QtWidgets.QLineEdit(str(v))
                    # TODO: Handle the `level` keyword here
                    # this should be synchronized across objects
                    aa.editingFinished.connect(lambda aa=aa, k=k:  plotopts.__setitem__(k, type(plotopts[k])(aa.text())))
                    layout.addWidget(aa)
                    dialog.addLayout(layout)

    def update_level(self, level):
        """
        Updates the number of events for each object in accordance with level
        """
        # crazy high intial values so that the new value is always lower
        num_events = 100_000
        newIdx = 100_000
        for (plotobj, plotopts) in zip(self.plotobjs, self.plotopts):
            nn, _newIdx = plotobj.plot(self.index, getNumEvents=True, **plotopts)
            num_events = min(num_events, nn)
            newIdx = min(newIdx, _newIdx)
        self.numEvents = num_events
        self.currentIndex.setText(str(newIdx))
        self.updateIndex()

    def update_index(self, new_index):
        index = self.index
        if 0 <= new_index < self.numEvents:
            index = new_index
        else:
            index = self.index

        self.index = index

    def gonext(self):
        self.update_index(self.index+1)
        self.currentIndex.setText(str(self.index))
        self.plot()

    def plot(self):
        """
        Call plot for each object with the current plot index.
        """
        for _ax in self.fig.axes:
            _ax.clear()
        for (i, plotobj) in enumerate(self.plotobjs):
            plotobj.plot(self.index, ax=self.fig.axes[i], **self.plotopts[i])

        for (i, plotobj) in enumerate(self.plotobjs):
            # explicitly set the limits based on shared
            ax = self.fig.axes[i]
            if self.linkxaxes[i] != i:
                # since x/y-lims appears to be fixed by sharex/sharey
                # here we epxlicitly set them based on datalimits of
                # the axes that this axis is linked to
                sharex = self.fig.axes[self.linkxaxes[i]]
                x_trf = ax.xaxis.get_transform()
                dl = sharex.dataLim
                x0, x1 = x_trf.transform(dl.intervalx)
                xr = x1-x0
                x0 -= 0.05*xr
                x1 += 0.05*xr
                ax.set_xlim(x0, x1)
            if self.linkyaxes[i] != i:
                sharey = self.fig.axes[self.linkyaxes[i]]
                ax.set_ylim(sharey.dataLim.y0, sharey.dataLim.y1)

        self.canvas.draw()
        self.repaint()

    def goprev(self):
        self.update_index(self.index-1)
        self.currentIndex.setText(str(self.index))
        self.plot()

    def updateIndex(self):
        self.update_index(int(self.currentIndex.text()))
        self.currentIndex.setText(str(self.index))  # Update the index shown
        for _ax in self.fig.axes:
            _ax.clear()
        for (i, plotobj) in enumerate(self.plotobjs):
            plotobj.plot(self.index, ax=self.fig.axes[i], **self.plotopts[i])
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
