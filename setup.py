from setuptools import setup, find_packages
from os.path import join as pjoin, dirname
from glob import glob
import sys

sys.path.append(pjoin(dirname(__file__),'conversion'))
from _version import __version__

requirements= open('requirements.txt').read().split()

setup(name='conversion',
    version=__version__,
    description='Python utility scripts for MRI processing',
    author='Tashrif Billah',
    author_email='tbillah@bwh.harvard.edu, tashrifbillah@gmail.com',
    url='https://github.com/pnlbwh/conversion',
    license='MIT License',
    install_requires=requirements,
    scripts=['conversion/nhdr_write.py', 'conversion/nifti_write.py'],
    packages=find_packages(exclude=('*tests*',)),
    package_data={'conversion':[pjoin('tests','*'), pjoin('tests','data','*'), pjoin('data','*')]},
    data_files=[('share/doc/conversion/data',glob(pjoin('data','*')))],
    project_urls={'Tracker':'https://github.com/pnlbwh/conversion/issues',
                   'Documentation':'https://github.com/pnlbwh/conversion/README.md'},
    python_requires='>=3')
