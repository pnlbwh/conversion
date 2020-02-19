![](Misc/pnl-bwh-hms.png)

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.2584003.svg)](https://doi.org/10.5281/zenodo.2584003) [![Python](https://img.shields.io/badge/Python-3.6-green.svg)]() [![Platform](https://img.shields.io/badge/Platform-linux--64%20%7C%20osx--64%20%7C%20win--64-orange.svg)]() [![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()


Table of Contents
=================

   * [Conversion](#conversion)
   * [Citation](#citation)
   * [Installation](#installation)
   * [Tests](#tests)
   * [Example usage](#example-usage)
   * [Acknowledgement](#acknowledgement)

Table of Contents created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)

# Conversion

This repository contains various mri conversion/modification scripts. Most importantly, it has reliable NRRD<-->NIFTI
conversion modules that replace `DWIConvert/ConvertBetweenFileFormats`. All the scripts require python>=3 interpreter
and makes use of [dipy](https://nipy.org/dipy).

Each of the following scripts has command line interface. Type `python script.py --help` to see their functionality.

| Script  | Function |
| ------------- | ------------- |
| nhdr_write.py | NIFTI-->NHDR conversion  |
| nifti_write.py | NRRD/NHDR-->NIFTI conversion  |
| Nrrd2Nhdr.py | NRRD-->NHDR conversion  |
| nhdr_data_file.py | Correct 'data file' in NHDR to be relative  |
| grad_remove.py | Remove gradients from DWMRI  |
| grad_avg.py | Average repeated gradients in DWMRI  |
| dwi_quality.py | Find various quality attributes of DWMRI  |

In addition, most of the functions can be imported in Python.


Developed by Tashrif Billah, Sylvain Bouix, and Yogesh Rathi, Brigham and Women's Hospital (Harvard Medical School).
A research paper writing is in progress on the [conversion methods](https://drive.google.com/open?id=10Z-qpGJugASmlx_un8M2KVOdFpYZtA9T).


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


Install from source using pip/python:

It will install the `conversion` package and dependencies in 
`miniconda3/lib/python3.x/site-packages/` directory.

```
git clone https://github.com/pnlbwh/conversion.git
cd conversion
pip install . # or python setup.py install --prefix /HOME/miniconda3/
```

Note: If you do not have ANTs, use [conda install -c pnlbwh ants](https://anaconda.org/pnlbwh/ants) 
to install ANTs. Also, you can build [ANTs](https://github.com/ANTsX/ANTs) from source. Either way, make sure 
ANTs commands are in your path. For `conda install -c pnlbwh ants`, ANTs commands should be in 
`miniconda3/pkgs/ants-2.2.0-0/bin` and `miniconda3/bin/antsRegistration`. If needed, use 
`export PATH=$PATH:miniconda3/pkgs/ants-2.2.0-0/bin` to put all the commands in your path.


After installation is complete, launch ipython/python and you should be able to do the following:

```
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

```
cd conversion
python -m unittest discover -v conversion/tests
```


# Example usage

On python:

```
import conversion
conversion.nhdr_write('dwi.nii.gz', 'dwi.bval', 'dwi.bvec', 'dwi.nhdr')
```

On the command line:

`nhdr_write --help`

```
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


`dwi_quality.py --help`

```
This script finds various DWMRI quality attributes:

 1. min_i{(b0<Gi)/b0} image and its mask
 2. negative eigenvalue mask
 3. fractional anisotropy FA, mean diffusivity MD, and mean kurtosis MK
 4. masks out of range FA, MD, and MK
 5. prints histogram for specified ranges
 6. gives a summary of analysis
 7. performs ROI based analysis:
    labelMap is defined in template space
    find b0 from the dwi
    register t2 MNI to dwi through b0
    find N_gradient number of stats for each label
    make a DataFrame with labels as rows and stats as columns

Looking at the attributes, user should be able to infer quality of the DWMRI and
changes inflicted upon it by some process.

Usage:
    dwi_quality.py [SWITCHES]

Meta-switches:
    -h, --help                                Prints this help message and quits
    --help-all                                Prints help messages of all sub-commands and quits
    -v, --version                             Prints the program's version and quits

Switches:
    --bval VALUE:ExistingFile                 bval for nifti image
    --bvec VALUE:ExistingFile                 bvec for nifti image
    --fa VALUE:str                            [low,high] (include brackets, no space), fractional anisotropy values outside the range are
                                              masked; the default is [0,1]
    -i, --input VALUE:ExistingFile            input nifti/nrrd dwi file; required
    -l, --labelMap VALUE:ExistingFile         labelMap in standard space
    -m, --mask VALUE:ExistingFile             input nifti/nrrd dwi file; required
    --md VALUE:str                            [low,high], (include brackets, no space), mean diffusivity values outside the range are
                                              masked; the default is [0,0.0003]
    --mk VALUE:str                            [low,high] (include brackets, no space), mean kurtosis values outside the range are masked,
                                              requires at least three shells for dipy model; the default is [0,0.3]
    -n, --name VALUE:str                      labelMap name
    -o, --outDir VALUE:ExistingDirectory      output directory; the default is input directory
    -t, --template VALUE:ExistingFile         t2 image in standard space (ex: T2_MNI.nii.gz)

```


# Acknowledgement

Developed by Tashrif Billah, Sylvain Bouix, and Yogesh Rathi, Brigham and Women's Hospital (Harvard Medical School).
In addition, we sincerely acknowledge feedback provided by Chris Rorden, Steve Piper, and Isaiah Norton.
