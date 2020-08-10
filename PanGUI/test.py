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
        self.setidx = [0 for i in range(self.data.shape[0])]
        self.current_idx = None

    def plot(self, i=None, getNumEvents=False, getLevels=False, getPlotOpts=False, ax=None, **kwargs):
        """
        This function showcases the structure of a plot function that works with PanGUI.
        """
        # define the plot options that this function understands
        plotopts = {"show": True, "factor": 1.0, "level": "trial","overlay": False,
                    "second_axis": False, "seeds": {"seed1": 1.0, "seed2": 2.0},
                    "color": DPT.objects.ExclusiveOptions(["red","green"], 0)}
        if getPlotOpts:
            return plotopts

        # Extract the recognized plot options from kwargs
        for (k, v) in plotopts.items():
            plotopts[k] = kwargs.get(k, v)

        if getNumEvents:
            # Return the number of events avilable
            if plotopts["level"] == "trial":
                return self.data.shape[0], 0
            elif plotopts["level"] == "cell":
                if i is not None:
                    nidx = self.setidx[i]
                else:
                    nidx = 0
                return np.max(self.setidx)+1, nidx
            elif plotopts["level"] == "all":
                return 1, 0
        if getLevels:        
            # Return the possible levels for this object
            return ["trial", "cell", "all"]
        
        if plotopts["level"] == "all":
            idx = range(self.data.shape[0])
        elif plotopts["level"] == "cell":
            idx = np.asarray(self.setidx) == i
        else:
            idx = i
        if ax is None:
            ax = gca()
        if not plotopts["overlay"]:
            ax.clear()

        if plotopts["show"]:
            data = self.data[idx, :].T
            if len(data.shape)==2:
                data = data.mean(1)
            f = plotopts["factor"]
            pcolor = plotopts["color"].selected()
            ax.plot(f*data, color=pcolor)
            ax.axvline(plotopts["seeds"]["seed1"])
            ax.axvline(plotopts["seeds"]["seed2"])

            if plotopts["second_axis"]:
                ax2 = ax.twinx()
                ax2.plot(0.5*self.data[i, :].T, color="black")
        return ax

    def append(self, obj):
        DPObject.append(self, obj)
        self.data = np.concatenate((self.data, obj.data), axis=0)


def test_same_obj():
    data1 = np.random.random((10, 1000))
    pp1 = PlotObject(data1, normpath=False)
    pp1.dirs = ["session01/array01/channel001/cell01"]
    _pp1 = PlotObject(data1, normpath=False)
    _pp1.dirs = ["session01/array01/channel001/cell01"]
    pp1.append(_pp1)
    ppg = PanGUI.create_window([pp1, pp1])

def test(linkaxes=True):
    data1 = np.random.random((10, 1000))
    data2 = np.random.random((10, 2000))
    data3 = np.random.random((10, 3000))
    pp1 = PlotObject(data1, normpath=False)
    pp1.dirs = ["session01/array01/channel001/cell01"]
    pp2 = PlotObject(data2, normpath=False)
    pp2.dirs = ["session01/array01/channel001/cell01"]
    pp3 = PlotObject(data3, normpath=False)
    pp3.dirs = ["session01/array01/channel001/cell01"]

    _pp1 = PlotObject(data1, normpath=False)
    _pp1.dirs = ["session01/array01/channel001/cell01"]
    pp1.append(_pp1)

    _pp2 = PlotObject(data2, normpath=False)
    _pp2.dirs = ["session01/array01/channel001/cell02"]
    pp2.append(_pp2)

    _pp3 = PlotObject(data3, normpath=False)
    _pp3.dirs = ["session01/array01/channel001/cell02"]
    pp3.append(_pp3)

    if linkaxes:
        ppg = PanGUI.create_window([pp1, pp2, pp3], linkxaxes=[0, 0, 0],
                                   linkyaxes=[0, 0, 0], factor=0.1, color="green")
    else:
        ppg = PanGUI.create_window([pp1, pp2, pp3], factor=0.1, color="green")
    return ppg


def test_single():
    data1 = np.random.random((10, 1000))
    pp1 = PlotObject(data1, normpath=False)
    ppg = PanGUI.create_window(pp1)
