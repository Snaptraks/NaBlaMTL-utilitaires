import numpy as np
import pandas as pd
from io import StringIO
import json
import requests
import pkg_resources

    
# MWDD_table = pkg_resources.resource_stream(__name__, 'MWDD_table.json')
# MWDD_table = json.load(MWDD_table)
MWDD_table = None
    

def get_MWDD_info(name):
    """Retourne un dict avec les parametres de l'etoile donnee en input."""
    global MWDD_table
    if MWDD_table is None:
        r = requests.get('http://montrealwhitedwarfdatabase.org/table.json')
        MWDD_table = r.json()
    
    for entry in MWDD_table['data']:
        try:
            namelist = entry['allnames']+entry['wdid']+entry['name']
        except KeyError:
            namelist = entry['allnames']+entry['wdid']
            
        if name.lower().replace(' ', '') in namelist.lower().replace(' ', ''):
            return entry
            

def get_MWDD_wdid(name):
    """Retourne l'identifiant unique d'une etoile dans MWDD."""
    
    return get_MWDD_info(name)['wdid']
    

def get_MWDD_spectra(name):
    """Retourne un dict contenant tous les spectres de l'etoile demandee dans
    MWDD."""
    
    output = {}
    wdid = get_MWDD_wdid(name)
    site = 'http://montrealwhitedwarfdatabase.org/WDs/'
    tar = site+wdid+'/spectlist.txt'
    tar = tar.replace(' ', '%20')
    spectlist = requests.get(tar)
    if spectlist.status_code == 200:
        f = spectlist.content.decode('utf-8')
    else:
        return None
        
    f = f.replace(' ', '%20').replace(r'\n', ' ').replace("'", '')
    listspec = f.split()
    
    for spec in listspec:
        
        req = requests.get(site+wdid.replace(' ', '%20')+'/'+spec)
        
        if req.status_code == 200:
            spectrum = req.text
        else:
            print('Spectrum {} not found.'.format(spec))
            continue
            
        data = pd.read_csv(StringIO(spectrum), sep = ',', skiprows = 1)
        output[spec.replace('%20', '_')] = data[['wavelength', 'flux']].values.T
        
    return output
