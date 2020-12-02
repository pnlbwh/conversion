#!/usr/bin/env python

import numpy as np
import argparse
import os, warnings, sys
# with warnings.catch_warnings():
#     warnings.filterwarnings("ignore", category=FutureWarning)
import nibabel as nib

PRECISION= 17
np.set_printoptions(precision= PRECISION, suppress= True, floatmode= 'maxprec')

from conversion.bval_bvec_io import read_bvecs, read_bvals, bvec_scaling

def matrix_string(A):
    # A= np.array(A)
    
    A= str(A.tolist())
    A= A.replace(', ',',')
    A= A.replace('],[',') (')
    return '('+A[2:-2]+')'
    
def find_mf(F):

    R= F/np.linalg.norm(F,axis=0)
    
    return R

def nhdr_write(nifti, bval, bvec, nhdr):

    print('Converting ', nifti)

    if nifti.endswith('.nii.gz'):
        encoding = 'gzip'
    elif nifti.endswith('.nii'):
        encoding = 'raw'
    else:
        raise ValueError('Invalid nifti file')

    img = nib.load(nifti)
    hdr = img.header

    if not nhdr:
        nhdr = os.path.abspath(nifti).split('.')[0] + '.nhdr'
    elif not nhdr.endswith('nhdr'):
        raise AttributeError('Output file must be nhdr')
    else:
        nhdr = os.path.abspath(nhdr)

    dim = hdr['dim'][0]
    # if bval/bvec provided but nifti is 3D, raise warning
    if dim == 3 and (bval or bvec):
        warnings.warn('nifti image is 3D, ignoring bval/bvec files')

    dtype = hdr.get_data_dtype()
    numpy_to_nrrd_dtype = {
        'int8': 'int8',
        'int16': 'short',
        'int32': 'int',
        'int64': 'longlong',
        'uint8': 'uchar',
        'uint16': 'ushort',
        'uint32': 'uint',
        'uint64': 'ulonglong',
        'float32': 'float',
        'float64': 'double'
    }

    f = open(nhdr, 'w')
    console = sys.stdout
    sys.stdout = f

    print(f'NRRD0005\n# NIFTI-->NHDR transform by Tashrif Billah\n\
# See https://github.com/pnlbwh/conversion for more info\n\
# Complete NRRD file format specification at:\n\
# http://teem.sourceforge.net/nrrd/format.html\n\
type: {numpy_to_nrrd_dtype[dtype.name]}\ndimension: {dim}\nspace: right-anterior-superior')

    sizes = hdr['dim'][1:dim + 1]
    print('sizes: {}'.format((' ').join(str(x) for x in sizes)))

    spc_dir = hdr.get_best_affine()[0:3, 0:3]

    # most important key
    print('byteskip: -1')

    endian = 'little' if dtype.byteorder == '<' else 'big'
    print(f'endian: {endian}')
    print(f'encoding: {encoding}')
    print('space units: "mm" "mm" "mm"')

    spc_orig = hdr.get_best_affine()[0:3, 3]
    print('space origin: ({})'.format((',').join(str(x) for x in spc_orig)))
    print(f'data file: {os.path.basename(nifti)}')

    # define oldmin and oldmax when scl_slope and scl_inter are present
    scl_slope= img.dataobj.slope
    scl_inter= img.dataobj.inter
    if scl_slope!=1.0 or scl_inter!=0:
        info= np.iinfo(dtype)
        oldmin= info.min*scl_slope+scl_inter
        oldmax= info.max*scl_slope+scl_inter
        print(f'old min: {oldmin}')
        print(f'old max: {oldmax}')

    # print description
    if img.header['descrip']:
        print('# {}'.format(np.char.decode(img.header['descrip'])))

    if dim == 4:
        print(f'space directions: {matrix_string(spc_dir.T)} none')
        print('centerings: cell cell cell ???')
        print('kinds: space space space list')

        if bval and bvec:

            mf = find_mf(spc_dir)
            print(f'measurement frame: {matrix_string(mf.T)}')

            bvecs = read_bvecs(bvec, assume_normed= False)
            bvals = read_bvals(bval)

            print('modality:=DWMRI')

            b_max = max(bvals)
            print(f'DWMRI_b-value:={b_max}')
            for ind in range(len(bvals)):
                scaled_bvec = bvec_scaling(bvals[ind], bvecs[ind], b_max)
                print(f'DWMRI_gradient_{ind:04}:={scaled_bvec}')

        else:
            warnings.warn('nifti image is 4D, but bval/bvec files are not provided, assuming not a DWMRI')

    else:
        print(f'space directions: {matrix_string(spc_dir.T)}')
        print('centerings: cell cell cell')
        print('kinds: space space space')

    f.close()
    sys.stdout = console


def main():

    parser = argparse.ArgumentParser(description='NIFTI to NHDR conversion tool setting byteskip = -1')
    parser.add_argument('--nifti', type=str, required=True, help='nifti file')
    parser.add_argument('--bval', type=str, help='bval file')
    parser.add_argument('--bvec', type=str, help='bvec file')
    parser.add_argument('--nhdr', type=str, help='output nhdr file, nifti and nhdr should be in the same directory')

    args = parser.parse_args()
    nhdr_write(args.nifti, args.bval, args.bvec, args.nhdr)

if __name__ == '__main__':
    main()
