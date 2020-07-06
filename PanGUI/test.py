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

    def __init__(self, *args, **kwargs):
        DPObject.__init__(self, *args ,**kwargs)
        self.data = self.args["data"]
        self.title = self.args["title"]
        self.indexer = self.getindex("trial")
        self.setidx = np.zeros((self.data.shape[0],), dtype=np.int)
        self.current_idx = None

    def load(self):
        fname = os.path.join(self.name, self.ext)
        if os.path.isfile(fname):
            if self.ext == "mat":
                dd = mio.loadmat(fname, squeeze_me=True)

    def update_idx(self, i):
        return max(0, min(i, self.data.shape[0]-1))

    def plot(self, i=None, getNumEvents=False, getLevels=False, getPlotOpts=False, ax=None, **kwargs):
        plotopts = {"show": True, "factor": 1.0, "level": "trial","overlay": False,
                    "second_axis": False, "seeds": {"seed1": 1.0, "seed2": 2.0},
                    "color": DPT.objects.ExclusiveOptions(["red","green"], 0)}
        if getPlotOpts:
            return plotopts

        for (k, v) in plotopts.items():
            plotopts[k] = kwargs.get(k, v)

        if getNumEvents:
            # Return the number of events avilable
            if plotopts["level"] == "trial":
                return self.data.shape[0]
            elif plotopts["level"] == "all":
                return 1
        if getLevels:        
            # Return the possible levels for this object
            return ["trial","all"]
        
        if plotopts["level"] == "all":
            idx = range(self.data.shape[0])
        else:
            idx = i
        if ax is None:
            ax = gca()
        if not plotopts["overlay"]:
            ax.clear()

        if plotopts["show"]:
            f = plotopts["factor"]
            pcolor = plotopts["color"].selected()
            ax.plot(f*self.data[idx, :].T, color=pcolor)
            ax.axvline(plotopts["seeds"]["seed1"])
            ax.axvline(plotopts["seeds"]["seed2"])

            if plotopts["second_axis"]:
                ax2 = ax.twinx()
                ax2.plot(0.5*self.data[i, :].T, color="black")
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
