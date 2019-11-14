from matplotlib import rc_context
from cycler import cycler


def supermongo():
    return rc_context({
        'text.usetex' : True,

        'figure.figsize': (6, 6),
        'figure.facecolor': 'none',
        'figure.edgecolor': 'none',
        'figure.autolayout': True,

        'font.size' : 11,
        'font.family': 'serif',

        'axes.labelsize': 'xx-large',
        'axes.facecolor': 'none',
        'axes.linewidth': 0.7,
        'axes.prop_cycle': cycler(color=[
            '#FF0000',
            '#00FF00',
            '#0000FF',
            '#00FFFF',
            '#FF00FF',
            '#FFFF00',
            '#000000',
            ]),

        'xtick.labelsize': 'medium',
        'xtick.top': True,
        'xtick.bottom': True,
        'xtick.direction': 'in',
        'xtick.major.size': 8,
        'xtick.minor.visible': True,
        'xtick.minor.size': 3,

        'ytick.labelsize': 'medium',
        'ytick.left': True,
        'ytick.right': True,
        'ytick.direction': 'in',
        'ytick.major.size': 8,
        'ytick.minor.visible': True,
        'ytick.minor.size': 3,

        'lines.markersize': 4,
        'lines.linewidth': 0.8,
        'lines.markeredgewidth': 0.2,

        'legend.numpoints': 1,
        'legend.frameon': False,
        'legend.handletextpad': 0.3,
        'legend.scatterpoints': 1,
        'legend.handlelength': 2,
        'legend.handleheight': 0.1,

        'savefig.dpi': 300,
        'savefig.facecolor': 'none',
        'savefig.edgecolor': 'none',
        })
