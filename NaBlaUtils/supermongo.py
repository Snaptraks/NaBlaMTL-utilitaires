from matplotlib import rc_context
from cycler import cycler


def supermongo():
    """Context manager to emulate the style of the SuperMongo plotting
    library. Font is still not quite there yet.

    Usage:
    x = <data>
    y = <other data>
    with supermongo():
        fig, ax = plt.subplots()
        ax.plot(x, y)
        fig.savefig('filename')
    """
    return rc_context({
        'axes.facecolor': 'none',
        'axes.labelpad': 18.0,
        'axes.labelsize': 'large',
        'axes.linewidth': 0.6,
        'axes.prop_cycle': cycler(color=[
            '#FF0000',
            '#00FF00',
            '#0000FF',
            '#00FFFF',
            '#FF00FF',
            '#FFFF00',
            '#000000',
            ]),

        'backend': 'GTK3AGG',

        'figure.autolayout': True,
        'figure.edgecolor': 'none',
        'figure.facecolor': 'none',
        'figure.figsize': (6, 6),

        'font.family': 'serif',
        'font.stretch': 'extra-expanded',
        'font.size' : 12,
        'font.weight': 'bold',

        'legend.frameon': False,
        'legend.handleheight': 0.1,
        'legend.handlelength': 2,
        'legend.handletextpad': 0.3,
        'legend.numpoints': 1,
        'legend.scatterpoints': 1,

        'lines.linewidth': 0.5,
        'lines.markeredgewidth': 0.2,
        'lines.markersize': 4,

        'mathtext.cal': 'cursive',
        'mathtext.fontset': 'cm',

        'savefig.dpi': 300,
        'savefig.edgecolor': 'none',
        'savefig.facecolor': 'none',

        'text.usetex' : True,

        'xtick.bottom': True,
        'xtick.top': True,
        'xtick.direction': 'in',
        'xtick.labelsize': 'medium',
        'xtick.major.pad': 5,
        'xtick.major.size': 5,
        'xtick.major.width': 0.6,
        'xtick.minor.size': 2,
        'xtick.minor.visible': True,
        'xtick.minor.width': 0.6,

        'ytick.left': True,
        'ytick.right': True,
        'ytick.direction': 'in',
        'ytick.labelsize': 'medium',
        'ytick.major.pad': 5,
        'ytick.major.size': 5,
        'ytick.major.width': 0.6,
        'ytick.minor.size': 2,
        'ytick.minor.visible': True,
        'ytick.minor.width': 0.6,
        })
