from setuptools import setup, find_packages
from os.path import join as pjoin
from glob import glob

requirements= open('requirements.txt').read().split()
# print(requirements)

setup(name='conversion',
    version='2.2',
    description='Python utility scripts for MRI processing',
    author='Tashrif Billah',
    author_email='tbillah@bwh.harvard.edu, tashrifbillah@gmail.com',
    url='https://github.com/pnlbwh/conversion',
    license='MIT License',
    install_requires=requirements,
    packages=find_packages(exclude=('*tests*',)),
    package_data={'conversion':[pjoin('tests','*'), pjoin('tests','data','*'), pjoin('data','*')]},
    data_files=[('share/doc/conversion/data',glob(pjoin('data','*')))],
    project_urls={'Tracker':'https://github.com/pnlbwh/conversion/issues',
                   'Documentation':'https://github.com/pnlbwh/conversion/README.md'},
    python_requires='>=3')
