import numpy as np
import pandas as pd
from io import StringIO
import json
import requests


MWDD_table = None


def get_MWDD_info(name):
    """Return a dict with the parameters of the star with given name."""

    global MWDD_table
    if MWDD_table is None:
        r = requests.get('http://montrealwhitedwarfdatabase.org/table.json')
        MWDD_table = r.json()

    for entry in MWDD_table['data']:
        try:
            namelist = entry['allnames'] + entry['wdid'] + entry['name']
        except KeyError:
            namelist = entry['allnames'] + entry['wdid']

        if name.lower().replace(' ', '') in namelist.lower().replace(' ', ''):
            return entry


def get_MWDD_wdid(name):
    """Return the unique identifier of a star in the MWDD."""

    return get_MWDD_info(name)['wdid']


def get_MWDD_spectra(name):
    """
    Return a dict contaning all the spectra in the MWDD of the
    requested star.
    """
    output = {}
    wdid = get_MWDD_wdid(name)
    site = 'http://montrealwhitedwarfdatabase.org/WDs/'
    tar = site + wdid + '/spectlist.txt'
    tar = tar.replace(' ', '%20')
    spectlist = requests.get(tar)
    if spectlist.status_code == 200:
        f = spectlist.content.decode('utf-8')
    else:
        return None

    f = f.replace(' ', '%20').replace(r'\n', ' ').replace("'", '')
    listspec = f.split()

    for spec in listspec:

        req = requests.get(site + wdid.replace(' ', '%20') + '/' + spec)

        if req.status_code == 200:
            spectrum = req.text
        else:
            print('Spectrum {} not found.'.format(spec))
            continue

        data = pd.read_csv(StringIO(spectrum), sep=',', skiprows=1)
        output[spec.replace('%20', '_')] = data[[
            'wavelength', 'flux']].values.T

    return output
