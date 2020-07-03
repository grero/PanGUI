import PanGUI
import DataProcessingTools as DPT
from DataProcessingTools.objects import DPObject
from pylab import gcf, gca
import numpy as np
import scipy
import scipy.io as mio
import os


class PlotObject(DPObject):
    argsList = ["data", ("title", "test")]
    level = "trial"

    def __init__(self,*args, **kwargs):
        DPObject.__init__(self, *args ,**kwargs)
        self.data = self.args["data"]
        self.title = self.args["title"]
        self.plotopts = {"show": True, "factor": 1.0,
                         "seeds": {"seed1": 1.0, "seed2": 2.0},
                         "color": DPT.objects.ExclusiveOptions(["red","green"], 0)}
        self.indexer = self.getindex("trial")
        self.setidx = np.zeros((self.data.shape[0],), dtype=np.int)
        self.current_idx = None

    def getlevels(self):
        return ["trial"]

    def load(self):
        fname = os.path.join(self.name, self.ext)
        if os.path.isfile(fname):
            if self.ext == "mat":
                dd = mio.loadmat(fname, squeeze_me=True)

    def update_idx(self, i):
        return max(0, min(i, self.data.shape[0]-1))

    def plot(self, i, ax=None, overlay=False):
        self.current_idx = i
        if ax is None:
            ax = gca()
        if not overlay:
            ax.clear()
        if self.plotopts["show"]:
            f = self.plotopts["factor"]
            pcolor = self.plotopts["color"].selected()
            ax.plot(f*self.data[i, :].T, color=pcolor)
            ax.axvline(self.plotopts["seeds"]["seed1"])
            ax.axvline(self.plotopts["seeds"]["seed2"])
        return ax


def test(linkaxes=True):
    data1 = np.random.random((10, 1000))
    data2 = np.random.random((10, 1000))
    pp1 = PlotObject(data1, normpath=False)
    pp1.dirs = ["session01/array01/channel001/cell01"]
    pp2 = PlotObject(data2, normpath=False)
    pp1.dirs = ["session01/array01/channel001/cell02"]
    if linkaxes:
        ppg = PanGUI.create_window([pp1, pp2], linkxaxes=[0, 0],
                                   linkyaxes=[0, 0])
    else:
        ppg = PanGUI.create_window([pp1, pp2])
    return ppg


def test_single():
    data1 = np.random.random((10, 1000))
    pp1 = PlotObject(data1)
    ppg = PanGUI.create_window(pp1)
