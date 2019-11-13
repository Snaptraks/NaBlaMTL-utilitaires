import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import re
from os.path import basename
import pkg_resources

from . import constants as sc
from .. import fortranformat as ff


class Spectre(object):
    def __init__(self, wav, flux, info):
        self.wav = wav
        self.flux = flux
        self.data = np.asarray([wav, flux])
        # self.info = {'imodel': info[0],
                     # 'inu'   : info[1]}
        self.imodel, self.inu = info
    
    
def spectre_test62(f):
    """Lecture d'un fichier spectre synthétique de test62,
    avec le package fortranformat.
    """
    
    format_wav  = ff.FortranRecordReader('(10f8.2)')
    format_flux = ff.FortranRecordReader('(6e12.5)')
        
    wav = []
    flux = []
    npts = int(f.readline()) # nombre de points de fréquence
    
    while len(wav) < npts:
        wav += format_wav.read(f.readline())
    wav = np.array(wav[:npts])
    
    test = f.readline() # Paramètres atmosphériques
    if len(test.split()) == 6:
        flux += format_flux.read(test)
    
    while len(flux) < npts:
        flux += format_flux.read(f.readline())
    flux = np.array(flux[:npts])
    
    return wav, flux
    

def spectre_csv(f):
    """Lecture d'un fichier spectre d'un fichier csv en 2 colonnes."""
    skip = 0
    while True:
        try:    
            wav, flux = np.loadtxt(f, delimiter = ',',
                              skiprows = skip, unpack = True)
        
        except ValueError:
            # Si les première lignes ont un en-tête
            skip += 1
            
        else:
            break
            
    return wav, flux
    

def spectre_tsv(f):
    """Lecture d'un fichier spectre en 2 colonnes."""
    skip = 0
    while True:
        try:    
            wav, flux = np.loadtxt(f, skiprows = skip, unpack = True)
        
        except ValueError:
            # Si les première lignes ont un en-tête
            skip += 1
            
        else:
            break
            
    return wav, flux
    

# def spectre_tsv3(f):
    # """ Lecture d'un fichier spectre en 3 colonnes (avec incertitudes sur flux)"""
    # try:
        # wav, flux, dflux = np.loadtxt(f, unpack = True)
    
    # except ValueError:
        # # Format TLUSTY, avec D comme format scientifique au lieu de E
        # f.seek(0)
        # D2E = lambda s: s.replace(b'D', b'E')
        # reg = re.compile(b'\d\.\d*-\d{3}')
        # addD = lambda s: D2E(s.replace(b'-', b'D-')) if reg.search(s) else D2E(s)
        # convert = {0: D2E,
                   # 1: addD}
                   
        # wav, flux, dflux = np.loadtxt(f, unpack = True, converters = convert)
 
    
    # return wav,flux
    
    
def spectre_tsv3(f):
    """Lecture d'un fichier spectre en 3 colonnes
    (avec incertitudes sur flux).
    """
    
    skip = 0
    while True:
        try:    
            wav, flux, dflux = np.loadtxt(f, skiprows = skip, unpack = True)
        
        except ValueError:
            # Si les première lignes ont un en-tête
            skip += 1
            
        else:
            break
            
    return wav, flux
    
    
def spectre_sdss_fits(f):
    """Lecture d'un fichier spectre .fits du SDSS."""
    hdul = fits.open(f)
    
    if 'SDSS' in hdul[0].header['TELESCOP']:
        # .fits from SDSS
        data = hdul[1].data
        
        # log10(wav) dans les .fits
        wav = 10.**data.field(1) # Angstrom
        
        # flux F_lambda en unités de 1e-17 erg/...
        flux = data.field(0)*1e-17 # erg/cm^2/s/Ang
        
        # c_ang = vitesse de la lumière en angstrom / s
        # flux *= wav**2/sc.c_ang # erg/cm^2/s/Hz
        
        hdul.close()
        return wav, flux
            
    else:
        raise Exception('.fits format inconnu')
    

def spectre_etrange(f):
    """Lecture d'un fichier spectre Fortran imprime en 5 ou 7 colonnes."""
    end = False
    while not end:
        try:
            line = f.readline().split()
            wavnew = [float(w) for w in line]
            wav = np.append(wav,wavnew)
            prevwav = wavnew[-1]
        except:
            end = True
            aflux = f.readlines()
            for line in aflux:
                line = re.sub('-10\d', 'e-100', line)
                flux = np.append(flux, line.rstrip().split())
                
    wav, flux = np.array(wav), np.array(flux)
    return wav, flux
    

def spec_info(inputfile,imodel,inu,teff):
    if imodel:
        types = 'modele'
    else:
        types = 'observation'
    if inu:
        unites = 'f_nu'
    else:
        unites = 'f_lambda'
    print(basename(inputfile)+' interprete comme '+types+' en '+unites)
    if imodel:
        print('Teff = '+str(int(teff)))
        
        
def load_spectre(inputfile):
    """Trouve le format du fichier inputfile, puis utilise la bonne méthode
    pour lire le fichier, et retourne le spectre wav, flux, ainsi que les
    flags imodel et inu.
    """
    
    if inputfile.endswith('fits'):
        wav, flux = spectre_sdss_fits(inputfile)
        imodel = False
        inu = False
    else:
        f = open(inputfile, 'r')
        # Lecture du header
        try:
            nn = int(f.tell())
            f.readline()
        except:
            pass
        # Lire la première ligne
        f.readline()
        # Vérifier le format dans la deuxième ligne
        test = f.readline()
        f.seek(0) # rewind jusqu'au début
        # Lecture des donnees
        if (len(test.split())==10) or (len(test.split())==6): # test62
            wav, flux = spectre_test62(f) 
            imodel = True
            inu = True
        elif(len(test.split(','))==2 or len(test.split(','))==4): # csv
            wav, flux = spectre_csv(f)
            imodel = False
            inu = False
        elif(len(test.split())==2): # tsv
            wav, flux = spectre_tsv(f)
            imodel = False
            inu = False
        elif(len(test.split())==3): # tsv avec incertitudes
            wav, flux = spectre_tsv3(f)
            imodel = False
            inu = False
        elif(len(test.split())==5 or len(test.split())==7): # format etrange
            wav, flux = spectre_etrange(f)
            imodel = False
            inu = False
        else:
            # print('Erreur dans plot_spectre')
            # print('Format inconnu pour '+inputfile)
            raise ValueError('Format inconnu pour '+inputfile)
        f.close()
        # flux = np.array([float(ff) for ff in flux])
        
    # return wav, flux, (imodel, inu)
    return Spectre(wav, flux, (imodel, inu))

        
def normalisation(wav, flux):
    """Normalisation du spectre à la valeur maximale du flux, 
    pour avoir tout les spectres sous le même ordre de grandeur.
    """
    
    return flux / flux.max() # flux maximal = 1

    # flux_norm = flux[wav>wav_norm][0]
    # return flux / flux_norm
    
    
def load_lines():
    """Lecture de la liste de raies, et retourne un dict avec l'ion en clé
    et la liste (array) de raies de cet ion en valeur.
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
        

def plot_spectre(filelist, figname = None, IDlines = None):
    """Trace les spectres dans la liste filelist.
    
    Si figname = None, retourne une fenêtre interactive
    Si un string est donné, enregistre la figure sous figname
    Si IDlines = None, ne met pas l'identification des raies sur la figure
    Si IDlines = str, on transforme comme IDlines = [str]
    Si IDlines = list, il faut que les items dans la liste soient le
    symbole atomique d'un élément (ex. Ca pour calcium)
    Si IDlines = 'All', alors on trace toutes les raies (les 200+, à éviter)
    """
        
    if not isinstance(filelist, list):
        filelist = [filelist]

    # Matplotlib plots
    fig, ax = plt.subplots()
    ax.minorticks_on()
    
    ax.set_xlabel('Longueur d\'onde ' + r'($\AA$)')
    ax.set_ylabel(r'$F_\nu$ ' + '(normalisé)')

    for i,inputfile in enumerate(filelist):
    
        # On lit le spectre
        # wav, flux, (imodel, inu) = load_spectre(inputfile)
        spectre = load_spectre(inputfile)
        wav, flux = spectre.data
        imodel = spectre.imodel
        inu = spectre.inu
        
        # Detection des unites
        if np.mean(wav) > 1e10:
            # wav en fréquence
            wav = sc.c_ang / wav
        if not imodel and np.mean(flux)<1e-20:
            inu = True
        # Conversion de f_lambda a f_nu
        if not inu:
            flux *= wav*wav/sc.c_ang

        teff = (-np.trapz(flux,x=sc.c_ang/wav)/sc.sigma*4.0*np.pi)**0.25
        # spec_info(inputfile,imodel,inu,teff)
        
        flux = normalisation(wav, flux)
        ax.plot(wav, flux, label = basename(inputfile))
        
    # Crée la légende
    ax.legend()
    
    # Si des éléments ont été fournis
    if IDlines:
    
        # setup pour la figure
        xlims = ax.get_xlim()
        tick_ymax = 0.05
    
        # On lit la liste de raies
        linedict = load_lines()
    
        # Si on a juste un élément, on transforme en list
        if isinstance(IDlines, str):
            IDlines = [IDlines]
            
        # On sélectionne les ions que l'on veut identifier
        matches = []
        for ion in IDlines:
            matches += [k for k in linedict if re.match(ion+r'[IV]+', k)]
        
        # Si on demande toutes les raies
        if 'All' in IDlines:
            matches = linedict.keys()
                
        # Pour chaque ion
        for k in matches:
            
            # Pour chaque raie de l'ion
            for l in linedict[k]:
                
                # On trace une ligne verticale
                ax.axvline(l, ymin = 0, ymax = tick_ymax, c='k')
                
                # Et on indique l'ion au dessus
                trans = ax.get_xaxis_transform()
                ax.text(x = l, y = tick_ymax+0.01,
                        s = k,
                        ha = 'center',
                        transform = trans,
                        clip_on = True)
                    
        # On remet les limites précédentes
        ax.set_xlim(xlims)
            
    if figname is None:
        plt.show(fig)
    else:
        fig.savefig(figname)
