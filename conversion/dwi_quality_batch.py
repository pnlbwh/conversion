#!/usr/bin/env python

# from conversion.dwi_quality import quality
from plumbum import cli
from os.path import dirname, join, basename, abspath, isdir
from os import mkdir
from shutil import rmtree
import psutil
import multiprocessing
import pandas as pd
import nibabel as nib
import numpy as np
from conversion import parse_labels, read_caselist, num2str
from subprocess import check_call
SCRIPTDIR=dirname(__file__)

def dwi_quality_wrapper(imgPath, maskPath, bvalFile, bvecFile,
                        mk_low_high, fa_low_high, md_low_high, out_dir, name, template, labelMap):
        
    if bvalFile and bvecFile:
        check_call((' ').join([f'{SCRIPTDIR}/dwi_quality.py',
                '-i', imgPath,'-m', maskPath, '--bval', bvalFile, '--bvec', bvecFile,
                '--mk', mk_low_high, '--fa', fa_low_high, '--md', md_low_high,
                '-o', out_dir, '-n', name, '-t', template, '-l', labelMap]), shell= True)
    else:
        check_call((' ').join([f'{SCRIPTDIR}/dwi_quality.py',
                '-i', imgPath,'-m', maskPath,
                '--mk', mk_low_high, '--fa', fa_low_high, '--md', md_low_high,
                '-o', out_dir, '-n', name, '-t', template, '-l', labelMap]), shell= True)

def summarize_csvs(imgs, labelMapFile, qcDir, labelName, out_csv):

    # extract case names from imgs
    cases=[]
    for imgPath in imgs:
        cases.append(basename(imgPath).split('.')[0])

    # extract region names from labelMap
    outLabelMap = nib.load(labelMapFile).get_data()
    labels = np.unique(outLabelMap)[1:]
    regions = parse_labels(labels).values()

    # define dataFrame
    # reference: https://jakevdp.github.io/PythonDataScienceHandbook/03.05-hierarchical-indexing.html
    index = pd.MultiIndex.from_product([regions, cases], names=['region', 'case'])
    dfsummary= pd.DataFrame(index=index, columns= ['FA_mean', 'FA_std', 'MD_mean', 'MD_std',
                                                   'AD_mean', 'AD_std', 'RD_mean', 'RD_std',
                                                   'total_{min_i(b0-Gi)<0}', 'total_evals<0',
                                                   'MK_mean', 'MK_std'])

    # read csvs, append to summary
    for imgPath, case in zip(imgs, cases):
        prefix= basename(imgPath).split('.')[0]
        csvPath = join(dirname(imgPath), qcDir, f'{prefix}_{labelName}_stat.csv')

        print('Reading ', csvPath)
        df= pd.read_csv(csvPath)
        df= df.set_index('region')
        idx= pd.IndexSlice
        for region in regions:
            dfsummary.loc[region, idx[case]]= [num2str(x) for x in df.loc[region]]

    dfsummary.to_csv(out_csv)
    print('See project summary', abspath(out_csv))


class quality_batch(cli.Application):
    """
    This script finds various DWMRI quality attributes for a batch of data:

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

    The quality attributes across subjects in the batch are exported into a csv/txt file.
    Looking at the attributes, user should be able to infer quality of the DWMRI and
    changes inflicted upon it by some process.
    """

    imagelist= cli.SwitchAttr(['-i', '--input'], help='csv/txt file with first column for dwi'
                        'and 2nd column for mask: dwi1,mask1\ndwi2,mask2\n...'
                        'for nifti dwi, .bval and .bvec files should have same prefix as that of the dwi'
                        'accepts both nrrd/nifti format for each pair of (dwi,mask)', mandatory= True)

    mk_low_high= cli.SwitchAttr('--mk', help='[low,high] (include brackets, no space), '
                'mean kurtosis values outside the range are masked, requires at least three shells for dipy model'
                , default=f'[0,0.3]')

    fa_low_high= cli.SwitchAttr('--fa', help='[low,high] (include brackets, no space), '
                'fractional anisotropy values outside the range are masked', default=f'[0,1]')

    md_low_high= cli.SwitchAttr('--md', help='[low,high], (include brackets, no space), '
                'mean diffusivity values outside the range are masked', default=f'[0,0.0003]')

    template= cli.SwitchAttr(['-t', '--template'], cli.ExistingFile, help='t2 image in standard space (ex: T2_MNI.nii.gz)')
    labelMap= cli.SwitchAttr(['-l', '--labelMap'], cli.ExistingFile, help='labelMap in standard space')
    name= cli.SwitchAttr(['-n', '--name'], help='labelMap name')
    qcDir = cli.SwitchAttr(['-d', '--qcDir'], help='folder to be created in dwi image directory where results are saved',
                           default='qualityAnalysis')

    out_csv= cli.SwitchAttr(['-o', '--output'], help='summary csv/txt file', mandatory= True)

    N_proc = cli.SwitchAttr('--nproc',
            help= 'number of processes/threads to use (-1 for all available, may slow down your system)', default= 4)


    def main(self):

        self.template= str(self.template)
        self.labelMap= str(self.labelMap)

        imgs, masks = read_caselist(self.imagelist)

        if int(self.N_proc)==-1:
            self.N_proc= psutil.cpu_count()

        pool= multiprocessing.Pool(int(self.N_proc))
        for imgPath, maskPath in zip(imgs, masks):
            imgPath= imgPath
            inPrefix= imgPath.split('.')[0]
            
            bvalFile= None
            bvecFile= None
            if imgPath.endswith('.nii') or imgPath.endswith('.nii.gz'):
                bvalFile = inPrefix + '.bval'
                bvecFile = inPrefix + '.bvec'

            out_dir= join(dirname(imgPath), self.qcDir)

            if isdir(out_dir):
                # force re-run
                rmtree(out_dir)
            mkdir(out_dir)
            pool.apply_async(func= dwi_quality_wrapper, args= (imgPath, maskPath, bvalFile, bvecFile,
                self.mk_low_high, self.fa_low_high, self.md_low_high, out_dir, self.name, self.template, self.labelMap))

        pool.close()
        pool.join()

        summarize_csvs(imgs, str(self.labelMap), self.qcDir, self.name, self.out_csv)


if __name__ == '__main__':
    quality_batch.run()
