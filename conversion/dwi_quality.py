#!/usr/bin/env python

from plumbum import cli, local
import os
import warnings
# with warnings.catch_warnings():
#     warnings.filterwarnings("ignore", category=FutureWarning)
import nibabel as nib
from dipy.reconst import dki, dti
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from dipy.segment.mask import applymask
from dipy.core.gradients import check_multi_b

import nrrd
import pandas as pd
import numpy as np
PRECISION= 5
np.set_printoptions(precision= PRECISION, suppress= True, floatmode= 'maxprec')

from conversion import nrrd_bvals_bvecs
from conversion import parse_labels
from conversion.antsUtil import antsReg, applyXform
from conversion import num2str

eps= 2.204e-16
inf= 65535.

def save_map(outFile, img, affine= None, hdr= None):

    if outFile.endswith('.nii.gz') or outFile.endswith('.nii'):
        out = nib.Nifti1Image(img, affine= affine)
        nib.save(out, outFile)
    else:
        nrrd.write(outFile, img,
                   header={'space directions': hdr['space directions'][:3, :3],
                           'space': hdr['space'], 'kinds': ['space', 'space', 'space'],
                           'centerings': ['cell', 'cell', 'cell'], 'space origin': hdr['space origin']})


def hist_calc(a, bins):
    hist_string= []
    N= len(bins)
    for i in range(N-1):
        hist_string.append(f'{bins[i]} <--> {bins[i+1]}')

    temp= np.histogram(a, bins=bins)[0]
    hist= temp.astype('float')/a.size

    try:
        hist[np.isnan]= 0
    except:
        pass

    print('%20s : %s' %('Bins','Density'))
    for i in range(N-1):
        print('%20s : %.5f' %(hist_string[i],hist[i]))

    return hist

def mask_calc(M, interval):
    "Masks out of interval values in M"

    a= M<interval[0]
    b= M>interval[1]

    C= a | b
    return C*1

def form_bins(interval):

    # interval= []
    if interval[0]*interval[1]<0:
        interval.append(0)
        if max(interval)>1:
            interval.append(1)
        if min(interval)<-1:
            interval.append(-1)

    else:
        interval= [interval[0], np.mean(interval), interval[1]]

    interval.sort()

    return interval


class quality(cli.Application):
    """
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
    """

    imgFile= cli.SwitchAttr(['-i', '--input'], cli.ExistingFile, mandatory=True, help='input nifti/nrrd dwi file')
    maskFile= cli.SwitchAttr(['-m', '--mask'], cli.ExistingFile, mandatory=True, help='input nifti/nrrd mask file')
    bvalFile= cli.SwitchAttr('--bval', cli.ExistingFile, help='bval for nifti image')
    bvecFile= cli.SwitchAttr('--bvec',  cli.ExistingFile, help='bvec for nifti image')

    mk_low_high= cli.SwitchAttr('--mk', help='[low,high] (include brackets, no space), '
                'mean kurtosis values outside the range are masked, requires at least three shells for dipy model'
                , default=f'[0,0.3]')

    fa_low_high= cli.SwitchAttr('--fa', help='[low,high] (include brackets, no space), '
                'fractional anisotropy values outside the range are masked', default=f'[0,1]')

    md_low_high= cli.SwitchAttr('--md', help='[low,high], (include brackets, no space), '
                'mean diffusivity values outside the range are masked', default=f'[0,0.0003]')

    out_dir = cli.SwitchAttr(['-o', '--outDir'], cli.ExistingDirectory, help='output directory', default='input directory')

    template= cli.SwitchAttr(['-t', '--template'], cli.ExistingFile, help='t2 image in standard space (ex: T2_MNI.nii.gz)')
    labelMap= cli.SwitchAttr(['-l', '--labelMap'], cli.ExistingFile, help='labelMap (atlas) in standard space')
    lut = cli.SwitchAttr('--lut', cli.ExistingFile,
                         help='look up table for specified labelMap (atlas), default: FreeSurferColorLUT.txt')
    name= cli.SwitchAttr(['-n', '--name'], help='labelMap name (e.g WhiteMatter, GrayMatter etc.)')

    def main(self):

        self.imgFile= str(self.imgFile)
        self.maskFile= str(self.maskFile)

        self.mk_low_high= [float(x) for x in self.mk_low_high[1:-1].split(',')]
        self.mk_low_high.sort()
        self.fa_low_high = [float(x) for x in self.fa_low_high[1:-1].split(',')]
        self.fa_low_high.sort()
        self.md_low_high = [float(x) for x in self.md_low_high[1:-1].split(',')]
        self.md_low_high.sort()
        hdr= None
        affine= None


        if not self.out_dir:
            self.out_dir= os.path.dirname(self.imgFile)

        outPrefix= os.path.join(self.out_dir, os.path.basename(self.imgFile).split('.')[0])


        if self.imgFile.endswith('.nii.gz') or self.imgFile.endswith('.nii'):
            bvals, bvecs = read_bvals_bvecs(self.bvalFile, self.bvecFile)
            outFormat='.nii.gz'

            img= nib.load(self.imgFile)
            data = img.get_data()

            affine= img.affine
            grad_axis= 3
            if len(data.shape)!=4:
                raise AttributeError('Not a valid dwi, check dimension')


        elif self.imgFile.endswith('.nrrd') or self.imgFile.endswith('.nhdr'):

            img = nrrd.read(self.imgFile)
            data = img[0]
            hdr = img[1]

            outFormat='.nrrd'

            bvals, bvecs, b_max, grad_axis, N = nrrd_bvals_bvecs(hdr)

            # put the gradients along last axis
            if grad_axis != 3:
                data = np.moveaxis(data, grad_axis, 3)

        # provide the user a liberty to specify different file formats for dwi and mask
        if self.maskFile.endswith('.nii.gz') or self.maskFile.endswith('.nii'):
            mask_data = nib.load(self.maskFile).get_data()

        elif self.maskFile.endswith('.nrrd') or self.maskFile.endswith('.nhdr'):
            mask_data = nrrd.read(self.maskFile)[0]

        data= applymask(data, mask_data)

        gtab = gradient_table(bvals, bvecs)

        dtimodel= dti.TensorModel(gtab)
        dtifit= dtimodel.fit(data, mask_data)
        evals= dtifit.evals
        fa= dtifit.fa
        md= dtifit.md
        ad= dtifit.ad
        rd= dtifit.rd
        evals_zero= evals<0.
        evals_zero_mask= (evals_zero[...,0] | evals_zero[...,1] | evals_zero[...,2])*1


        mkFlag= check_multi_b(gtab,n_bvals=3)
        if mkFlag:
            dkimodel = dki.DiffusionKurtosisModel(gtab)
            dkifit = dkimodel.fit(data, mask_data)
            mk = dkifit.mk(0,3) # http://nipy.org/dipy/examples_built/reconst_dki.html

        else:
            warnings.warn("DIPY DKI requires at least 3 b-shells (which can include b=0), "
                             "kurtosis quality cannot be computed.")


        fa_mask= mask_calc(fa, self.fa_low_high)
        md_mask= mask_calc(md, self.md_low_high)

        where_b0s= np.where(bvals==0)[0]
        where_dwi= np.where(bvals!=0)[0]
        bse_data= data[...,where_b0s].mean(-1)
        b0File= outPrefix + '_b0' + outFormat
        save_map(b0File, bse_data, affine, hdr)

        # prevent division by zero during normalization
        bse_data[bse_data < 1] = 1.
        extend_bse = np.expand_dims(bse_data, grad_axis)
        extend_bse = np.repeat(extend_bse, len(where_dwi), grad_axis)
        curtail_dwi = np.take(data, where_dwi, axis=grad_axis)

        # 1 / b0 * min(b0 - Gi)
        minOverGrads = np.min(extend_bse - curtail_dwi, axis=grad_axis) / bse_data

        # another way to prevent division by zero: 1/b0 * min(b0-Gi) with condition at b0~eps
        # minOverGrads = np.min(extend_bse - curtail_dwi, axis=grad_axis) / (bse_data + eps)
        # minOverGrads[(bse_data < eps) & (minOverGrads < 5 * eps)] = 0.
        # minOverGrads[(bse_data < eps) & (minOverGrads > 5 * eps)] = 10.

        minOverGradsNegativeMask = (minOverGrads < 0) * 1

        # compute histograms
        print('\nminOverGrads (b0-Gi)/b0 histogram')
        bins= [-inf,0,inf]
        negative, _= hist_calc(minOverGrads, bins)

        print('\nevals<0 histogram')
        bins= [-inf,0,inf]
        hist_calc(evals, bins)

        print('\nfractional anisotropy histogram')
        bins= form_bins(self.fa_low_high)
        hist_calc(fa, bins)

        print('\nmean diffusivity histogram')
        bins= form_bins(self.md_low_high)
        hist_calc(md, bins)

        if mkFlag:
            print('\nmean kurtosis mask')
            bins = form_bins(self.mk_low_high)
            hist_calc(mk, bins)

        # save histograms
        print('\nCreating minOverGrads image ...')
        save_map(outPrefix + '_minOverGrads' + outFormat, minOverGrads, affine, hdr)
        print('\nCreating minOverGrads<0 mask ...')
        save_map(outPrefix + '_minOverGradsMask' + outFormat, minOverGradsNegativeMask.astype('short'), affine, hdr)

        print('\nCreating evals<0 mask ...')
        save_map(outPrefix + '_evalsZeroMask' + outFormat, evals_zero_mask.astype('short'), affine, hdr)


        if mkFlag:
            mk_mask = mask_calc(mk, self.mk_low_high)
            print('\nCreating mk image ...')
            save_map(outPrefix + '_MK' + outFormat, mk, affine, hdr)
            print('Creating mk out of range mask ...')
            save_map(outPrefix + '_MK_mask' + outFormat, mk_mask.astype('short'), affine, hdr)

        print('\nCreating fa image ...')
        save_map(outPrefix + '_FA' + outFormat, fa, affine, hdr)
        print('Creating fa out of range mask ...')
        save_map(outPrefix + '_FA_mask' + outFormat, fa_mask.astype('short'), affine, hdr)

        print('\nCreating md image ....')
        save_map(outPrefix + '_MD' + outFormat, md, affine, hdr)
        print('Creating md out of range mask ...')
        save_map(outPrefix + '_MD_mask' + outFormat, md_mask.astype('short'), affine, hdr)


        # conclusion
        N_mask= mask_data.size
        print('\n\nConclusion: ')
        print('The masked dwi has %.5f%% voxels with values less than b0'
              % (negative * 100))
        print('The masked dwi has %.5f%% voxels with negative eigen value' % (evals_zero_mask.sum() / N_mask * 100))
        print('The masked dwi has %.5f%% voxels with FA out of [%f,%f]'
              % (fa_mask.sum() / N_mask * 100, self.fa_low_high[0], self.fa_low_high[1]))
        print('The masked dwi has %.5f%% voxels with MD out of [%f,%f]'
              % (md_mask.sum() / N_mask * 100, self.md_low_high[0], self.md_low_high[1]))
        if mkFlag:
            print('The masked dwi has %.5f%% voxels with MK out of [%f,%f]'
                  % (mk_mask.sum() / N_mask*100, self.mk_low_high[0], self.mk_low_high[1]))


        # perform roi based analysis
        if self.template and self.labelMap:
            antsReg(b0File, self.maskFile, self.template, outPrefix)
            warp = outPrefix+ '1Warp.nii.gz'
            trans = outPrefix+ '0GenericAffine.mat'
            outLabelMapFile = outPrefix + '_labelMap.nii.gz'
            applyXform(self.labelMap, b0File, warp, trans, outLabelMapFile, interp='NearestNeighbor')
            rm= local['rm']
            rm(warp, trans,
                  outPrefix+'Warped.nii.gz', outPrefix+'1InverseWarp.nii.gz', outPrefix+'InverseWarped.nii.gz')

            outLabelMap = nib.load(outLabelMapFile).get_data()
            labels = np.unique(outLabelMap)[1:]
            label2name = parse_labels(labels, self.lut._path)

            print('Creating ROI based statistics ...')
            stat_file= outPrefix + f'_{self.name}_stat.csv'

            df= pd.DataFrame(columns= ['region','FA_mean','FA_std','MD_mean','MD_std',
                                                'AD_mean','AD_std','RD_mean','RD_std',
                                                'total_{min_i(b0-Gi)<0}','total_evals<0',
                                                'MK_mean','MK_std',])

            for i,label in enumerate(label2name.keys()):
                roi = outLabelMap == int(label)
                _roi= np.where(roi>0)

                fa_roi = applymask(fa, roi)
                md_roi = applymask(md, roi)
                ad_roi = applymask(ad, roi)
                rd_roi = applymask(rd, roi)
                mk_roi = np.zeros(roi.shape)

                minOverGradsNegativeMask_roi = applymask(minOverGradsNegativeMask, roi)
                evals_zero_mask_roi = applymask(evals_zero_mask, roi)

                if mkFlag:
                    mk_roi = applymask(mk, roi)

                properties= [num2str(x) for x in [fa_roi[_roi].mean(), fa_roi[_roi].std(),
                                                  md_roi[_roi].mean(), md_roi[_roi].std(),
                                                  ad_roi[_roi].mean(), ad_roi[_roi].std(),
                                                  rd_roi[_roi].mean(), rd_roi[_roi].std(),
                                                  minOverGradsNegativeMask_roi[_roi].sum(), evals_zero_mask_roi[_roi].sum(),
                                                  mk_roi[_roi].mean(), mk_roi[_roi].std()]
                             ]


                df.loc[i]= [label2name[label]]+ properties

            df= df.set_index('region')
            # print(df)
            df.to_csv(stat_file)
            print('See ', os.path.abspath(stat_file))

if __name__=='__main__':
    quality.run()

