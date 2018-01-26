# Simple driver implementation, whose main purpose is testing.

from datetime import datetime as dt
import engine.solver as FDTD
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy
import engine.boundaries as bounds
from matplotlib.colors import LogNorm

import engine.sources as sources

g = FDTD.Grid(301,301)
for i in range(5):
    pos = numpy.random.random(2)*300
    parms = 2*(numpy.random.random(4) - 0.5)
    eff = 0.5
    g.add_source(
        sources.SourceDipole(
            (int(pos[0]), int(pos[1])),
            sources.PulseGaussian(
                1 * (1 + eff*parms[0]),
                300 * (1 + eff*parms[1]),
                100 * (1 + eff*parms[2]),
                1/40 * (1 + eff*parms[3])
            )
        )
    )

g.set_boundaries(xm=bounds.PEC(), xp=bounds.PEC(), ym=bounds.PEC(), yp=bounds.PEC())
fig = plt.figure()
plt.subplots_adjust(top=0.8)
ax = plt.axes(xlim=(-0.5,300.5), ylim=(-0.5,300.5))
ax.set_aspect('equal')

data = g.get_field(2)._data
data = numpy.array(list(map(lambda x: 0*x+1e-10, data))) # TODO: clean this mess up
im = ax.imshow(numpy.abs(data), cmap=plt.get_cmap('jet'), norm=LogNorm(vmin=1e-4, vmax=2, clip=True))
g.get_field(2)._data = data
cbar = plt.colorbar(im, ax=ax)

time = [dt.now(), dt.now()]
elaps_gen = [0] * 50
elaps_rend = [0] * 50
txt = "frame {:4d}\nTimes: {:.2f} ms (gen.), {:.2f} ms (rend.)\nFPS: {:.1f}"
text0 = ax.text(150,370, txt.format(0, sum(elaps_gen)/len(elaps_gen), sum(elaps_rend)/len(elaps_rend), 0))
text0.set_horizontalalignment("center")
text0.set_verticalalignment("top")
text0.set_color('r')
text0.set_fontsize(16)

def init():
    data = g.get_field(2)._data
    im.set_data(numpy.abs(data))
    return [im]

def update(i):
    def to_msec(x):
        return x.seconds * 1000 + x.microseconds/1000
    time[0] = dt.now()
    elaps_rend.pop(0)
    elaps_rend.append(to_msec(time[0] - time[1]))
    g.step(i)
    time[1] = dt.now()
    elaps_gen.pop(0)
    elaps_gen.append(to_msec(time[1] - time[0]))
    data = g.get_field(2)._data
    im.set_data(numpy.abs(data))
    text0.set_text(txt.format(
        i,
        sum(elaps_gen)/len(elaps_gen),
        sum(elaps_rend)/len(elaps_rend),
        1000 / (sum(elaps_rend)/len(elaps_rend) + sum(elaps_gen)/len(elaps_gen))
    ))
    return [im, text0]

anim = animation.FuncAnimation(
    fig,
    update,
    init_func=init,
    frames=800,
    repeat=False,
    interval=int(1000/30),
    blit=False
)

plt.show()

