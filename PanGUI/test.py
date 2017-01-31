import PanGUI
from pylab import gca
import numpy as np

class PlotObject():
    def __init__(self,data,title="Test windwow"):
        self.data = data
        self.title = title

    def plot(self,i,ax=None):
        if ax is None:
            ax = gca()
        ax.plot(self.data[i,:])
        return ax

def test():
    data = np.random.random((10, 1000))
    pp = PlotObject(data)
    ppg = PanGUI.create_window(PanGUI.Main, pp)


