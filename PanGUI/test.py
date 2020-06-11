import PanGUI
from pylab import gcf
import numpy as np
import scipy
import scipy.io as mio
import os


class DPVObject():
    def __init__(self):
        self.data = []


class PlotObject():
    def __init__(self, data, title="Test windwow", name="", ext="mat"):
        self.data = data
        self.title = title

    def load(self):
        fname = os.path.join(self.name, self.ext)
        if os.path.isfile(fname):
            if self.ext == "mat":
                dd = mio.loadmat(fname, squeeze_me=True)

    def update_idx(self, i):
        return max(0, min(i, self.data.shape[0]-1))

    def plot(self, i, fig=None):
        if fig is None:
            fig = gcf()
        if len(fig.axes) < 1:
            ax = fig.add_subplot(111)
        else:
            ax = fig.axes[0]
            ax.clear()
        ax.plot(self.data[i, :])
        return ax


def test():
    data = np.random.random((10, 1000))
    pp = PlotObject(data)
    ppg = PanGUI.create_window(pp)
