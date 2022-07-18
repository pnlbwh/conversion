#!/usr/bin/env python

import warnings
# with warnings.catch_warnings():
#     warnings.filterwarnings("ignore", category=FutureWarning)
import nibabel as nib

from conversion.bval_bvec_io import read_bvals, read_bvecs, write_bvals, write_bvecs, \
    bvec_scaling, nrrd_bvals_bvecs
import nrrd
import numpy as np
import argparse
import os

PRECISION= 17
np.set_printoptions(precision= PRECISION, suppress= True, floatmode= 'maxprec')

def grad_avg(imgFile, outFile, bvalFile= None, bvecFile= None):


    if imgFile.endswith('.nii.gz') or imgFile.endswith('.nii'):
        bvals= read_bvals(bvalFile)
        N= len(bvals)
        b_max= max(bvals)
        bvecs= read_bvecs(bvecFile)

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

        # put the gradients along last axis
        if grad_axis!=3:
            data= np.moveaxis(data, grad_axis, 3)

    bvals= np.array(bvals)
    bvecs= np.array(bvecs)
    print('Total input gradients ', len(bvals))
    # compute angles between bvecs, keep all the b0s, avg the rest alike ones
    compare_mask = N * [1]
    bvecs_new= []
    bvals_new= []
    data_new= []
    for i in range(N):
        if bvals[i] and compare_mask[i]:
            ind_same= [i]

            for j in range(i+1, N):
                if compare_mask[j]:
                    angle= np.arccos(np.clip(np.dot(bvecs[i], bvecs[j]),-1,1))*180/np.pi
                    if angle < 5:
                        # print(f'Degree angle between gradients {i} and {j}: {angle}')
                        ind_same.append(j)
                        compare_mask[j]= 0

            if len(ind_same)>=2:
                print('Averaging gradients: ', ind_same)
            data_new.append(np.mean(data[...,ind_same], axis= 3))
            temp= np.mean(bvecs[ind_same], axis= 0)
            bvecs_new.append(temp/np.linalg.norm(temp))
            bvals_new.append(np.round(np.mean(bvals[ind_same])))

        elif not bvals[i]:
            data_new.append(data[...,i])
            bvecs_new.append(bvecs[i])
            bvals_new.append(bvals[i])

    data_new= np.moveaxis(data_new, 0, -1)
    bvecs_new= np.array(bvecs_new)
    bvals_new= np.array(bvals_new)

    # write out the data, bvals, and bvecs
    if outFile.endswith('.nii.gz') or outFile.endswith('.nii'):
        out= nib.Nifti1Image(data_new, img.affine)
        nib.save(out, outFile)

        write_bvals(outFile.split('.')[0]+'.bval', bvals_new)
        write_bvecs(outFile.split('.')[0]+'.bvec', bvecs_new)
    else:
        if grad_axis!=3:
            data_new= np.moveaxis(data_new, 3, grad_axis)
        hdr_out['sizes'][grad_axis]= len(bvals_new)

        if outFile.endswith('.nhdr'):
            if 'data file' in hdr_out.keys():
                del hdr_out['data file']
            elif 'datafile' in hdr_out.keys():
                del hdr_out['datafile']

        for ind in range(len(bvals_new)):
            hdr_out['DWMRI_gradient_' + f'{ind:04}'] = bvec_scaling(bvals_new[ind], bvecs_new[ind], b_max)

        # Now delete the rest of the gradients
        for ind in range(len(bvals_new), len(bvals)):
            del hdr_out['DWMRI_gradient_' + f'{ind:04}']

        nrrd.write(outFile, data_new, header= hdr_out, compression_level = 1)

    if len(bvals)==len(bvals_new):
        print('No duplicate gradients, output same as input')
    else:
        print('After averaging, total output gradients ', len(bvals_new))


def main():

    parser = argparse.ArgumentParser(description='NIFTI/NRRD gradient averaging tool')
    parser.add_argument('-i', '--input', type=str, required=True, help='nifti/nrrd dwi image')
    parser.add_argument('--bval', type=str, help='bval file')
    parser.add_argument('--bvec', type=str, help='bvec file')
    parser.add_argument('-o', '--output', type=str, help='output nifti/nhdr file')

    args = parser.parse_args()

    inFile= os.path.abspath(args.input)
    outFile= args.output
    if not outFile:
        parts= inFile.split('.')
        outFile= parts[0]+ '_averaged.'+ ('.').join(ext for ext in parts[1: ])

    grad_avg(inFile, outFile, args.bval, args.bvec)

if __name__ == '__main__':
    main()
