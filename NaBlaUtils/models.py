import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import basename

from . import constants as sc


def _initDF():
    """Return an empty DataFrame with the columns already created."""
    columns = [
        'tauR',   # optical depth
        'z',      # geometrical depth
        'kappaR',  # Rosseland oppacity
        'NH+',    # population H+ (protons)
        'NH',  # hydrogen atom
               'NHe',  # helium
               'NH2',  # molecular hydrogen
               'sm',     # ?????
               'entr',   # entropy
               'P',      # pressure
               'T',      # temperature
               'Ne',     # electron population
               'rho',    # density
               'Mass',   # mass above the layer
               'Frad',   # flux fraction in radiation
               'Fconv',  # in convection
               'Ftot',   # total flux
        ]

    df = pd.DataFrame(columns=columns)

    return df


def _D2E(s):
    # todo: fix 1.000-100 -> 1.000E-100
    return s.replace(b'D', b'E')


def model_tlusty6(f):
    """Read models *.6 from TLUSTY.

    Return a dict with effective temperature, surface gravity, and a
    DataFrame with the different parameters of interest.
    """

    df = _initDF()  # empty DataFrame

    while True:
        # We search the appropriate lines in the file
        line = f.readline()
        if 'TEFF' in line:
            Teff = float(line.split()[-1])
        if 'LOG G' in line:
            logg = float(line.split()[-1])
        if 'TOTAL SURFACE FLUX' in line:
            break  # model is right under
    line = f.readline()  # the header
    f.readline()  # empty line

    conv = {}
    for i in range(len(line.split()) - 1):
        # converter 1.D+2 -> 1.E+2, for each column
        conv[i] = _D2E

    data = np.loadtxt(f, converters=conv, unpack=True)

    # Save in the DataFrame
    df['Mass'] = data[1]
    df['tauR'] = data[2]
    df['T'] = data[3]
    df['Ne'] = data[4]
    df['rho'] = data[5]
    df['P'] = data[6]
    df['Ftot'] = data[7]
    df['Frad'] = data[8]
    df['Fconv'] = data[9]

    return {'Teff': Teff, 'logg': logg, 'model': df}


def model_tlusty7(f):
    """temp"""

    raise NotImplementedError('https://i.imgur.com/10lkUdy.gif')


def model_test62(f):
    """Read models from test62 / geras.

    Return a dict with effective temperature, surface gravity, and a
    DataFrame with the different parameters of interest.
    """

    df = _initDF()  # empty DataFrame

    params = f.readline().split()  # Model's atmospheric parameters

    nq = int(params[1])
    Teff = float(params[3])
    logg = np.log10(float(params[5]))

    # abuncances line (test62) or other parameters (geras)
    test = f.readline().split()

    if len(test) == 3:
        # geras model
        f.readline()

    # for each layer, we read the line
    data = []
    for i in range(nq):
        data.append(np.fromstring(f.readline(), sep=' '))
    data = np.array(data).T

    # for each layer, we read the line
    df['tauR'] = data[0]
    df['kappaR'] = data[1]
    df['NH+'] = data[2]
    df['NH'] = data[3]
    df['NHe'] = data[4]
    df['NH2'] = data[5]

    f.readline()  # Model's atmospheric parameters
    f.readline()  # Abundances

    # for each layer, we read the line
    data = []
    for i in range(nq):
        data.append(np.fromstring(f.readline(), sep=' '))
    data = np.array(data).T

    # for each layer, we read the line
    df['sm'] = data[0]
    df['entr'] = data[2]
    df['P'] = data[3]
    df['T'] = data[4]
    df['Ne'] = data[5]

    # compute the density, based on hydrogen and helium
    density = df[['NH', 'NH+', 'NH2', 'NHe']] * np.array([1, 1, 2, 4])
    df['rho'] = density.sum(axis=1) / sc.N_A

    # compute geometric depth
    # s = integral( delta_tau / kappa / rho, from 0 to tau )
    kap_rho = df['kappaR'] * df['rho']
    dtau = df['tauR'].diff()
    df['z'] = (dtau / kap_rho).cumsum()

    return {'Teff': Teff, 'logg': logg, 'model': df}


def load_model(inputfile):
    """
    Determine the type of model (TLUSTY, test62, geras) and
    return the model's dict.
    """

    with open(inputfile, 'r') as f:

        test = f.readline().split()
        f.seek(0)

        if len(test) == 1:
            # Tlusty.6
            model = model_tlusty6(f)

        elif len(test) == 2:
            # Tlusty.7
            model = model_tlusty7(f)

        else:
            # test62 / geras
            model = model_test62(f)

    return model


def plot_model(filelist, figname=None, params=['T', 'P']):
    """
    Plot the structure of the models in filelist, for the parameters in params.

    If figname is None, open in an interactive window.
    If a str is given, save the figure under figname.

    params is a list of two different parameters of the atmospheric model,
    to plot against the optical depth.
    By default, plot temperature and pressure.

    params: 'tauR'  : optical depth
            'z'     : geometrical depth
            'kappaR': Rosseland oppacity
            'NH+'   : population H+ (protons)
            'NH'    :            hydrogen atom
            'NHe'   :            helium
            'NH2'   :            molecular hydrogen
            'sm'    : ?????
            'entr'  : entropy
            'P'     : pressure
            'T'     : temperature
            'Ne'    : electron population
            'rho'   : density
            'Mass'  : mass above the layer
            'Frad'  : flux fraction in radiation
            'Fconv' :               in convection
            'Ftot'  : total flux
    """

    # Labels for the y axis
    labels = {
        'tauR': r'$\tau_R$',
        'z': r'Geometrical depth (cm)',
        'kappaR': r'$\kappa_R',
        'NH+': r'$N_{H^+}$',
               'NH': r'$N_H$',
               'NHe': r'$N_{He}$',
               'NH2': r'$N_{HII}$',
               'sm': r'sm',
               'entr': r'S',
               'P': r'Pressure (dyn cm$^{-2}$)',
               'T': r'Temperature (K)',
               'Ne': r'$N_{e^-}$',
               'rho': r'Density (g cm$^{-3}$)',
               'Mass': r'Mass (g)',
               'Frad': r'Radiative Flux',
               'Fconv': r'Convective Flux',
               'Ftot': r'Total Flux',
        }

    if not isinstance(filelist, list):
        filelist = [filelist]

    assert len(params) == 2  # absolutely 2 parameters

    # Matplotlib plot
    fig, ax = plt.subplots(nrows=1, ncols=2)
    fig.subplots_adjust(wspace=0.3)
    ax[0].minorticks_on()
    ax[1].minorticks_on()

    for i, inputfile in enumerate(filelist):

        # Read the model
        model_dict = load_model(inputfile)

        Teff = model_dict['Teff']
        logg = model_dict['logg']
        model = model_dict['model']  # the DataFrame

        for p, param in enumerate(params):

            # If one parameter is unkown, raise an Exception
            if param not in model.columns:
                raise ValueError('Unknown parameter {}.'.format(param))

            if param in ('T', 'z', 'Frad', 'Fconv'):
                # Linear plot in y, log in x
                ax[p].semilogx(model['tauR'], model[param],
                               label=basename(inputfile))

            else:
                # log-log plot
                ax[p].loglog(model['tauR'], model[param],
                             label=basename(inputfile))

            ax[p].set_xlabel(r'$\tau_R$')
            ax[p].set_ylabel(labels[param])

    ax[0].legend()

    if figname is None:
        plt.show()
    else:
        fig.savefig(figname)

    plt.close(fig)
