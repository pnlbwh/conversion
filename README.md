![](Misc/pnl-bwh-hms.png)

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.2584003.svg)](https://doi.org/10.5281/zenodo.2584003) [![Python](https://img.shields.io/badge/Python-3.6-green.svg)]() [![Platform](https://img.shields.io/badge/Platform-linux--64%20%7C%20osx--64%20%7C%20win--64-orange.svg)]()

Developed by Tashrif Billah, Sylvain Bouix, and Yogesh Rathi, Brigham and Women's Hospital (Harvard Medical School).

Table of Contents
=================

   * [Introduction](#introduction)
   * [Citation](#citation)
   * [Installation](#installation)
   * [Tests](#tests)
   * [Example usage](#example-usage)
   * [Wiki](#wiki)
   * [Acknowledgement](#acknowledgement)

Table of Contents created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)


# Introduction

This repository contains various scripts for MRI modification and file format conversion. 
Most importantly, it has reliable NRRD<-->NIFTI conversion modules that replace `DWIConvert` and `ConvertBetweenFileFormats`. 
All the scripts require python>=3 interpreter.

Each of the following scripts has command line interface. Type `python script.py --help` to see their functionality.

| Script  | Function |
| ------------- | ------------- |
| nhdr_write.py | NIFTI-->NHDR conversion  |
| nifti_write.py | NRRD/NHDR-->NIFTI conversion  |
| Nrrd2Nhdr.py | NRRD-->NHDR conversion  |
| nhdr_data_file.py | Correct 'data file' in NHDR to be relative  |
| grad_remove.py | Remove gradients from DWMRI  |
| grad_avg.py | Average repeated gradients in DWMRI  |

In addition, most of the functions can be imported in `python`.

The details of file format conversion i.e. NRRD<-->NIFTI can be found [here](https://drive.google.com/file/d/10Z-qpGJugASmlx_un8M2KVOdFpYZtA9T/view?usp=sharing).


# Citation

If the package is useful in your research, please cite as below:

Billah, Tashrif; Bouix; Sylvain; Rathi, Yogesh; Various MRI Conversion Tools,
https://github.com/pnlbwh/conversion, 2019, DOI: 10.5281/zenodo.2584003



# Installation

The package requires python>=3 interpreter. If you do not have conda/python on your system,
download [Miniconda](https://conda.io/miniconda.html) (64/36-bit based on your environment).
You might find it useful to check the installation script usage:

```
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh -h
```

If you do not want to scroll through the license agreement, rather agree on them all, install as follows:
`./Miniconda3-latest-Linux-x86_64.sh -b`

It will install in `/HOME/miniconda3/` location as default. If a previous installation exists,
you can specify a different PREFIX using `-p` or use `-f` to overwrite existing installation.


To continue further, you should have conda/python in your system path:
`source /HOME/miniconda3/bin/activate`


Now let's install *conversion* package from source using `pip` or `python`:

```bash
git clone https://github.com/pnlbwh/conversion.git
cd conversion
pip install . # or python setup.py install --prefix /HOME/miniconda3/
```

The above will install the package and associated dependencies in 
`miniconda3/lib/python3.x/site-packages/` directory.

After installation is complete, launch ipython/python and you should be able to do the following:

```python
In [1]: import conversion
In [2]: dir(conversion)
Out[2]:
['__builtins__',
 '__cached__',
 '__doc__',
 '__file__',
 '__loader__',
 '__name__',
 '__package__',
 '__path__',
 '__spec__',
 '__version__',
 '_version',
 'bval_bvec_io',
 'bvec_scaling',
 'fs_label_parser',
 'grad_avg',
 'grad_remove',
 'nhdr_write',
 'nifti_write',
 'nrrd_bvals_bvecs',
 'parse_labels',
 'read_bvals',
 'read_bvecs',
 'read_grad_ind',
 'transpose',
 'write_bvals',
 'write_bvecs']

```


# Tests

Upon succesful installation, you can run tests as follows:

```bash
python -m unittest discover -v conversion/tests
```


# Example usage

On python:

```python
import conversion
conversion.nhdr_write('dwi.nii.gz', 'dwi.bval', 'dwi.bvec', 'dwi.nhdr')
```

On the command line:

`nhdr_write.py --help`

```bash
usage: nhdr_write.py [-h] --nifti NIFTI [--bval BVAL] [--bvec BVEC]
                     [--nhdr NHDR]

NIFTI to NHDR conversion tool setting byteskip = -1

optional arguments:
  -h, --help     show this help message and exit
  --nifti NIFTI  nifti file
  --bval BVAL    bval file
  --bvec BVEC    bvec file
  --nhdr NHDR    output nhdr file

```


# Wiki

1. Running tests from the correct directory

`python setup.py install` will install in `miniconda3/lib/python3.*/site-packages/conversion*/`

Then, if you attempt to run tests from a wrong directory:

```vim
cd conversion/conversion
python -m unittest discover -v tests/
```

[`test_file_conversion.py`](https://github.com/pnlbwh/conversion/blob/master/conversion/tests/test_file_conversion.py) : `from conversion.tests.util import *` will determine test data file names relative to the global installation, which is unwanted when test data are modified in the staging directory! So, always follow instruction in [Tests](#tests) to run them from the correct directory.

Also, beware of `discover` global import https://docs.python.org/3/library/unittest.html#test-discovery


# Acknowledgement

We sincerely acknowledge feedback provided by Chris Rorden, Steve Pieper, and Isaiah Norton.
