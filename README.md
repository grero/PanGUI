Introduction
------------
PanGUI offers a simple way of panning through a sequence of plots.

Installation
-----------

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

class PlotObj()
    def __init__(self):
        self.data = np.random.random((10, 1000))

    def plot(self, i, fig):
          if len(fig.axes) < 1:
              ax = fig.add_subplot(111)
          else:
              ax = fig.axes[0]
          ax.clear()
          ax.plot(data[i, :])

    def update_idx(self, index):
        return max(0, min(index, data.shape[0]-1))

app = PanGUI.create_window(PlotObj())
```
This will pop-up a plot window that plots the rows of `plotobj.data`. Clicking `prev` or `next` will step through the rows, while a specific row can be selected via the textfield.
