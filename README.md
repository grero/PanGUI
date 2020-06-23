Introduction
------------
PanGUI offers a simple way of panning through a sequence of plots.

Installation
-----------

pip install git+https://github.com/grero/DataProcessingTools.git
pip install git+https://github.com/grero/PanGUI.git

conda install --channel grero1980 pangui

Usage
------

```python
import PanGUI
PanGUI.test()
```

To create a panning window, use the ```create_window``` function, supply a ```plotobj``` object accepting two arguments; the first is an index to plot and the second is a ```matplotlib.figure``` instance to plot into.  

We can see how this works by examining the ```test``` function called above. First we generate some random data

```python
import DataProcessingTools as DPT

class PlotObj(DPT.objects.DPObject):
    def __init__(self):
        self.data = np.random.random((10, 1000))
        self.setidx = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1] 
        self.dirs = ["session01/array01/channel001/cell01",
                     "session01/array01/channel002/cell01"]

    def plot(self, i=None, ax=None):
        if ax is None:
            ax = gca()
        ax.clear()
        ax.plot(self.data[i, :].T)


app = PanGUI.create_window(PlotObj(), indexer="trial")
```
This will pop-up a plot window that plots the rows of `plotobj.data`. Clicking `prev` or `next` will step through the rows, while a specific row can be selected via the textfield.

Multiple objects can be plotted at the same time, like this:

```python
po1 = PlotObj()
po2 = PlotObj()
po3 = PlotObj()
po4 = PlotObj()
app = PanGUI.create_window([po1, po2, po3, po4], cols=2)
```

This creates a 2x2 grid of the 4 plot objects.
