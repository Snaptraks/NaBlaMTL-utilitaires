import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import re
from os.path import basename
import pkg_resources

from . import constants as sc
from . import fortranformat as ff


class Spectrum(object):
    def __init__(self, wav, flux, info):
        self.wav = wav
        self.flux = flux
        self.data = np.asarray([wav, flux])
        # self.info = {'imodel': info[0],
        # 'inu'   : info[1]}
        self.imodel, self.inu = info


def spectrum_test62(f):
    """Read a synthetic spectrum from the test62 code
    with the fortranformat package.
    """
    format_wav = ff.FortranRecordReader('(10f8.2)')
    format_flux = ff.FortranRecordReader('(6e12.5)')

    wav = []
    flux = []
    npts = int(f.readline())  # number of frequency points

    while len(wav) < npts:
        wav += format_wav.read(f.readline())
    wav = np.array(wav[:npts])

    test = f.readline()  # atmospheric parameters
    if len(test.split()) == 6:
        flux += format_flux.read(test)

    while len(flux) < npts:
        flux += format_flux.read(f.readline())
    flux = np.array(flux[:npts])

    return wav, flux


def spectrum_csv(f):
    """Read a spectrum in a csv 2-column file."""

    skip = 0
    while True:
        try:
            wav, flux = np.loadtxt(f, delimiter=',',
                                   skiprows=skip, unpack=True)

        except ValueError:
            # If the first lines have a header
            skip += 1

        else:
            break

    return wav, flux


def spectrum_tsv(f):
    """Read a spectrum in a 2 column file."""

    skip = 0
    while True:
        try:
            wav, flux = np.loadtxt(f, skiprows=skip, unpack=True)

        except ValueError:
            # If the first lines have a header
            skip += 1

        else:
            break

    return wav, flux


def spectrum_tsv3(f):
    """Read a spectrum in a 3 column file (with flux uncertainties)."""
    skip = 0
    while True:
        try:
            wav, flux, dflux = np.loadtxt(f, skiprows=skip, unpack=True)

        except ValueError:
            # If the first lines have a header
            skip += 1

        else:
            break

    return wav, flux


def spectrum_sdss_fits(f):
    """Read spectrum in a .fits file from SDSS."""

    hdul = fits.open(f)

    if 'SDSS' in hdul[0].header['TELESCOP']:
        # .fits from SDSS
        data = hdul[1].data

        # log10(wav) in the .fits
        wav = 10.**data.field(1)  # Angstrom

        # flux F_lambda in units of de 1e-17 erg/...
        flux = data.field(0) * 1e-17  # erg/cm^2/s/Ang

        # c_ang = speed of light in angstrom / s
        # flux *= wav**2/sc.c_ang # erg/cm^2/s/Hz

        hdul.close()
        return wav, flux

    else:
        raise Exception('Unknown .fits format.')


def spectrum_misc(f):
    """Read spectrum in a Fortran output file, saved in 5 or 7 columns."""

    end = False
    while not end:
        try:
            line = f.readline().split()
            wavnew = [float(w) for w in line]
            wav = np.append(wav, wavnew)
            prevwav = wavnew[-1]

        except BaseException:
            end = True
            aflux = f.readlines()
            for line in aflux:
                line = re.sub(r'-10\d', 'e-100', line)
                flux = np.append(flux, line.rstrip().split())

    wav, flux = np.array(wav), np.array(flux)
    return wav, flux


def spectrum_info(inputfile, imodel, inu, teff):
    if imodel:
        types = 'model'
    else:
        types = 'observation'

    if inu:
        units = 'f_nu'
    else:
        units = 'f_lambda'


def load_spectrum(inputfile):
    """Find the file format of inputfile, then use the right function to read
    the file, and return the spectrum (wav, flux) and the imodel and inu flags.
    """
    if inputfile.endswith('fits'):
        wav, flux = spectrum_sdss_fits(inputfile)
        imodel = False
        inu = False

    else:
        f = open(inputfile, 'r')
        # Read header
        try:
            nn = int(f.tell())
            f.readline()
        except BaseException:
            pass

        # Read first line
        f.readline()
        # Check format of second line
        test = f.readline()
        f.seek(0)  # rewind to begining

        # Read data
        if (len(test.split()) == 10) or (len(test.split()) == 6):  # test62
            wav, flux = spectrum_test62(f)
            imodel = True
            inu = True

        elif(len(test.split(',')) == 2 or len(test.split(',')) == 4):  # csv
            wav, flux = spectrum_csv(f)
            imodel = False
            inu = False

        elif(len(test.split()) == 2):  # tsv
            wav, flux = spectrum_tsv(f)
            imodel = False
            inu = False

        elif(len(test.split()) == 3):  # tsv with uncertainties
            wav, flux = spectrum_tsv3(f)
            imodel = False
            inu = False

        elif(len(test.split()) == 5 or len(test.split()) == 7):  # mics format
            wav, flux = spectrum_misc(f)
            imodel = False
            inu = False

        else:

            raise ValueError(f'Unknown format for {inputfile}.')

        f.close()

    return Spectrum(wav, flux, (imodel, inu))


def normalize(wav, flux):
    """Normalize the spectrum at the maximal value of the flux, to have all
    spectra at the same order of magnitude.
    """
    return flux / flux.max()  # maximum flux = 1

    # flux_norm = flux[wav>wav_norm][0]
    # return flux / flux_norm


def load_lines():
    """Read the line list, and return a dict with the ions as keys and
    an array of the lines of the ions as the values.
    """
    linelist = pkg_resources.resource_stream(__name__, 'lines.csv')
    linedict = {}

    for line in linelist.readlines():
        ion, wav = line.split(b',')
        ion = ion.decode('utf-8')
        wav = float(wav)

        try:
            linedict[ion].append(wav)

        except KeyError:
            linedict[ion] = [wav]

    for ion in linedict:
        linedict[ion] = np.array(linedict[ion])

    return linedict


def plot_spectrum(filelist, figname=None, IDlines=None):
    """Plot the spectra in the filelist.

    If figname is None, open the figure in interactive window.
    If figname is a string, save the figure under figname.
    If IDlines is None, do not identify the spectral lines on the figure.
    if IDlines is a string, transform it as length 1 list.
    If IDlines is a list, the elements need to be the atomic symbol of an
    element (ie. Ca for calcium).
    If IDlines = 'All', then plot all the spectral lines (over 200, to be
    avoided).
    """
    if not isinstance(filelist, list):
        filelist = [filelist]

    # Matplotlib plots
    fig, ax = plt.subplots()
    ax.minorticks_on()

    ax.set_xlabel(r'Wavelength ($\AA$)')
    ax.set_ylabel(r'$F_\nu$ (normalized)')

    for i, inputfile in enumerate(filelist):

        # Read the spectrum
        # wav, flux, (imodel, inu) = load_spectre(inputfile)
        spectrum = load_spectrum(inputfile)
        wav, flux = spectrum.data
        imodel = spectrum.imodel
        inu = spectrum.inu

        # Units detection
        if np.mean(wav) > 1e10:
            # wav in frequency
            wav = sc.c_ang / wav

        if not imodel and np.mean(flux) < 1e-20:
            inu = True

        # Conversion from f_lambda to f_nu
        if not inu:
            flux *= wav * wav / sc.c_ang

        teff = (-np.trapz(flux, x=sc.c_ang / wav) /
                sc.sigma * 4.0 * np.pi)**0.25

        flux = normalize(wav, flux)
        ax.plot(wav, flux, label=basename(inputfile))

    ax.legend()

    # If elements have been provided
    if IDlines is not None:

        # setup for the figure
        xlim = ax.get_xlim()
        tick_ymax = 0.05

        # Read the line list
        linedict = load_lines()

        # If only one element, convert to list
        if isinstance(IDlines, str):
            IDlines = [IDlines]

        # Select only the elements we want
        matches = []
        for ion in IDlines:
            matches += [k for k in linedict if re.match(ion + r'[IV]+', k)]

        # If all lines are requested
        if 'All' in IDlines:
            matches = linedict.keys()

        # For each ion
        for k in matches:

            # for each line of the ion
            for l in linedict[k]:

                # Plot vertical line
                ax.axvline(l, ymin=0, ymax=tick_ymax, c='k')

                # And label the element above it
                trans = ax.get_xaxis_transform()
                ax.text(
                    x=l,
                    y=tick_ymax + 0.01,
                    s=k,
                    ha='center',
                    transform=trans,
                    clip_on=True,
                    )

        # Set previous limits
        ax.set_xlim(xlim)

    if figname is None:
        plt.show()

    else:
        fig.savefig(figname)

    plt.close()
