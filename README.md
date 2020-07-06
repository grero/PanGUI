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

class PlotObject(DPObject):
    argsList = ["data", ("title", "test")]

    def __init__(self, *args, **kwargs):
        DPObject.__init__(self, *args ,**kwargs)
        self.data = self.args["data"]
        self.title = self.args["title"]
        self.indexer = self.getindex("trial")
        self.setidx = np.zeros((self.data.shape[0],), dtype=np.int)
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
                return self.data.shape[0]
            elif plotopts["level"] == "all":
                return 1
        if getLevels:        
            # Return the possible levels for this object
            return ["trial", "all"]
        
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

app = PanGUI.create_window(PlotObj())
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

Axes can be linked using the `linkxaxes` and `linkyaxes` keywords.

```python
app = PanGUI.create_window([po1, po2, po3, po4], cols=2,
                           linkxaxes=[0, 0, 2, 2))
```
This will link the x-axes of the first two objects together, and the x-axes of the second two objects. 
`linkxaxes` and `linkyaxes` should contain the index of the objects to which the axis should be linked. Specifying its own inde, like for the 1st and 3rd object in the above example, is a non-oeration, meaning they specify no link. In other words, the default state, with no axes linking, in the above example is `linkxaxes = [0,1,2,3]`.
