#!/usr/bin/env python

import warnings
# with warnings.catch_warnings():
#     warnings.filterwarnings("ignore", category=FutureWarning)
import nibabel as nib

from conversion.bval_bvec_io import read_bvals, read_bvecs, write_bvals, write_bvecs, \
    bvec_scaling, read_grad_ind, nrrd_bvals_bvecs
import nrrd
import numpy as np
import argparse
import os

PRECISION= 17
np.set_printoptions(precision= PRECISION, suppress= True, floatmode= 'maxprec')

def grad_remove(imgFile, outFile, qc_bad_indices= [], interval= [], bvalFile= None, bvecFile= None):

    print('Reading input ...')
    if imgFile.endswith('.nii.gz') or imgFile.endswith('.nii'):
        bvals= read_bvals(bvalFile)
        N= len(bvals)
        b_max= max(bvals)
        bvecs= read_bvecs(bvecFile, assume_normed= False)
        grad_axis= 3

        img= nib.load(imgFile)
        data = img.get_fdata()
        if len(data.shape)!=4:
            raise AttributeError('Not a valid dwi, check dimension')


    elif imgFile.endswith('.nrrd') or imgFile.endswith('.nhdr'):

        img= nrrd.read(imgFile)
        data= img[0]
        hdr= img[1]
        hdr_out= hdr.copy()

        bvals, bvecs, b_max, grad_axis, N= nrrd_bvals_bvecs(hdr)

    # qc index validity check
    for i in qc_bad_indices:
        if i<0 or i>N:
            raise IndexError(f'Index {i} is out of bound')

    shell_bad_indices=[]
    if interval:
        shell_bad_indices= [i for i in range(N) if bvals[i]>=interval[0] and bvals[i]<=interval[1]]
        if not shell_bad_indices:
            raise ValueError('No bval falls in the range')

    bad_indices= qc_bad_indices+shell_bad_indices
    bad_indices= list(set(bad_indices))

    print('Unwanted gradient indices: ', bad_indices)

    # delete volume
    data_new= np.delete(data, bad_indices, axis= grad_axis)
    # delete corresponding bval
    bvals_new= np.delete(bvals, bad_indices)
    # delete corresponding bvec
    bvecs_new= np.delete(bvecs, bad_indices, axis= 0)

    print('Writing output ...')
    if outFile.endswith('.nii.gz') or outFile.endswith('.nii'):
        out= nib.Nifti1Image(data_new, img.affine)
        nib.save(out, outFile)

        write_bvals(outFile.split('.')[0]+'.bval', bvals_new)
        write_bvecs(outFile.split('.')[0]+'.bvec', bvecs_new)
    else:

        hdr_out['sizes'][grad_axis]= len(bvals_new)


        if outFile.endswith('.nhdr'):
            try:
                del hdr_out['data file']
            except:
                del hdr_out['datafile']

        for ind in range(len(bvals_new)):
            hdr_out['DWMRI_gradient_' + f'{ind:04}'] = bvec_scaling(bvals_new[ind], bvecs_new[ind], b_max)

        # Now delete the rest of the gradients
        for ind in range(len(bvals_new), len(bvals)):
            del hdr_out['DWMRI_gradient_' + f'{ind:04}']

        nrrd.write(outFile, data_new, header= hdr_out, compression_level = 1)


    print('Writing complete, total output gradients ', len(bvals_new))


def main():

    parser = argparse.ArgumentParser(description='NIFTI/NRRD gradient removal tool')
    parser.add_argument('-i', '--input', type=str, required=True, help='nifti/nrrd dwi image')
    parser.add_argument('--bval', type=str, help='bval file')
    parser.add_argument('--bvec', type=str, help='bvec file')
    parser.add_argument('-q', '--qcFile', type=str, help='txt/csv file containing bad_indices of gradients to be removed, '
                        'gradients are 0 indexed, indices correspond to the original dwi,'
                        ' list can be comma, space, or newline separated')
    parser.add_argument('-r', '--range', type=str,
                        help='range of bvals to remove: [low,high] (include square brackets, no spaces)')
    parser.add_argument('-o', '--output', type=str, help='output nifti/nhdr file')

    args = parser.parse_args()

    inFile= os.path.abspath(args.input)
    outFile= args.output
    if not outFile:
        parts= inFile.split('.')
        outFile= parts[0]+ '_gradRemoved.'+ ('.').join(ext for ext in parts[1: ])


    qc_bad_indices= []
    interval= []

    if args.qcFile:
        qc_bad_indices= read_grad_ind(args.qcFile)

    if args.range:
        interval = args.range
        interval = [int(x) for x in interval[1:-1].split(',')]

    grad_remove(inFile, outFile, qc_bad_indices= qc_bad_indices, interval= interval, bvalFile= args.bval, bvecFile= args.bvec)


if __name__ == '__main__':
    main()