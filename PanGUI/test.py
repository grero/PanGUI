import PanGUI
from pylab import gcf
import numpy as np

class PlotObject():
    def __init__(self,data,title="Test windwow"):
        self.data = data
        self.title = title

    def plot(self,i,fig=None):
        if fig is None:
            fig = gcf()
        ax = fig.add_subplot(111)
        ax.plot(self.data[i,:])
        return ax

def test():
    data = np.random.random((10, 1000))
    pp = PlotObject(data)
    ppg = PanGUI.create_window(PanGUI.Main, pp)


