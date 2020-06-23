import PanGUI
import DataProcessingTools as DPT
from pylab import gcf
import numpy as np
import scipy
import scipy.io as mio
import os


class PlotObject(DPT.objects.DPObject):
    def __init__(self, data, title="Test windwow", name="", ext="mat"):
        self.data = data
        self.title = title
        self.dirs = [""]
        self.setidx = np.zeros((data.shape[0],), dtype=np.int)

    def load(self):
        fname = os.path.join(self.name, self.ext)
        if os.path.isfile(fname):
            if self.ext == "mat":
                dd = mio.loadmat(fname, squeeze_me=True)

    def update_idx(self, i):
        return max(0, min(i, self.data.shape[0]-1))

    def plot(self, i, ax=None, overlay=False):
        if ax is None:
            ax = gca()
        if not overlay:
            ax.clear()
        ax.plot(self.data[i, :].T)
        return ax


def test():
    data1 = np.random.random((10, 1000))
    data2 = np.random.random((10, 1000))
    pp1 = PlotObject(data1)
    pp1.dirs = ["session01/array01/channel001/cell01"]
    pp2 = PlotObject(data2)
    pp1.dirs = ["session01/array01/channel001/cell02"]
    ppg = PanGUI.create_window([pp1, pp2], indexer="trial")
    return ppg


def test_single():
    data1 = np.random.random((10, 1000))
    pp1 = PlotObject(data1)
    ppg = PanGUI.create_window(pp1)
