"""Some useful functions for data analysis."""

# Elements with the index as defined in the test62/geras atmospheric code
ELEMENTS = (
    ',C,N,O,F,Ne,Na,Mg,Al,Si,P,S,Cl,Ar,K,Ca,Sc,Ti,V,Cr,Mn,Fe,Co,Ni,Cu'
    ).split(',')

def fnu2flambda(arr):
    """Convert a spectrum from F_nu to F_lambda.

    Input
    -----
    arr : ndarray (2, n)
        Array containing the wavelength [0] and flux [1] of the spectrum.

    Output
    ------
    out : ndarray (2, n)
        Array containing the wavelength [0] and converted flux [1] of the
        spectrum.
    """
    fnu = arr[1] * sc.c_ang / arr[0]**2
    return np.asarray([arr[0], fnu])


def flambda2fnu(arr):
    """Convert a spectrum from F_nu to F_lambda.

    Input
    -----
    arr : ndarray (2, n)
        Array containing the wavelength [0] and flux [1] of the spectrum.

    Output
    ------
    out : ndarray (2, n)
        Array containing the wavelength [0] and converted flux [1] of the
        spectrum.
    """
    flambda = arr[1] * arr[0]**2 / sc.c_ang
    return np.asarray([arr[0], flambda])
