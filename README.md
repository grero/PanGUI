Introduction
------------
PanGUI offers a simple way of panning through a sequence of plots.

Installation
-----------

pip install git+https://github.com/grero/PanGUI.git

Usage
------

```python
import PanGUI
PanGUI.test()
```

To create a panning window, use the ```create_window``` function, supply a ```plotfunc``` function accepting two arguments; the first is an index to plot and the second is a ```matplotlib.figure``` instance to plot into.  

We can see how this works by examining the ```test``` function called above. First we generate some random data

```python
data = np.random.random((10, 1000))

def plotfunc(i, fig):
      if len(fig.axes) < 1:
          ax = fig.add_subplot(111)
      else:
          ax = fig.axes[0]
      ax.clear()
      ax.plot(data[i, :])

app = PanGUI.create_window(plotfunc, range(data.shape[0]))
```

Here we see that the plot function only receives an index telling it which row of ```data``` to plot. Note, though, that the second argument of ```create_window``` can be any iterable. Behind the scenes, PanGUI will step through the iterable, calling ```plotfunc``` with an element of the iterable as the first argument. This allows PanGUI to work with any sequence of "things", and it is up to the user to define how each element of a sequence should be plotted.
