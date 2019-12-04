"""
Python utility for data analysis and visualization of related to white dwarfs.

Package created Simon Blouin in collaboration with François Hardy.
"""

from .spectrums import plot_spectrum, load_spectrum, load_lines
from .models import plot_model, load_model
from .MWDD import get_MWDD_info, get_MWDD_spectra
from .supermongo import supermongo
from . import tools
