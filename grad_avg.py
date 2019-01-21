#!/usr/bin/env python

import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import nibabel as nib

from bval_bvec_io import read_bvals, read_bvecs, write_bvals, write_bvecs, bvec_scaling
import nrrd
import numpy as np
import argparse
import os

np.set_printoptions(suppress= True, floatmode= 'maxprec')

def avg(imgFile, outFile, bvalFile= None, bvecFile= None):


    if imgFile.endswith('.nii.gz') or imgFile.endswith('.nii'):
        bvals= read_bvals(bvalFile)
        b_max= max(bvals)
        bvecs= read_bvecs(bvecFile)

        img= nib.load(imgFile)
        data = img.get_data()
        if len(data.shape)!=4:
            raise AttributeError('Not a valid dwi, check dimension')


    elif imgFile.endswith('.nrrd') or imgFile.endswith('.nhdr'):

        img= nrrd.read(imgFile)
        data= img[0]
        hdr= img[1]
        hdr_out= hdr.copy()

        if hdr['dimension']==4:
            axis_elements= hdr['kinds']
        else:
            raise AttributeError('Not a valid dwi, check dimension')

        for i in range(4):
            if axis_elements[i] == 'list' or axis_elements[i] == 'vector':
                grad_axis= i
                break


        # put the gradients along last axis
        if grad_axis!=3:
            data= np.moveaxis(data, grad_axis, 3)

        b_max= float(hdr['DWMRI_b-value'])

        N= hdr['sizes'][grad_axis]
        bvals= np.empty(N, dtype= float)
        bvecs= np.empty((N,3), dtype= float)
        for ind in range(N):
            bvec = [float(num) for num in hdr[f'DWMRI_gradient_{ind:04}'].split()]
            L_2= np.linalg.norm(bvec)
            bvals[ind]= round(L_2 ** 2 * b_max)

            if L_2:
                bvecs[ind]= bvec/L_2
            else:
                bvecs[ind]= [0, 0, 0]

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

    avg(inFile, outFile, args.bval, args.bvec)

if __name__ == '__main__':
    main()
