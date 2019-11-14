from setuptools import setup, find_packages

setup(
    name='NaBlaUtils',
    version='0.2',
    description="Python utility for data analysis and visualization of related to white dwarfs.",
    url='https://github.com/Snaptraks/NaBlaMTL-utilitaires',
    package_data={'': ['lines.csv']},
    packages=find_packages()
    )
