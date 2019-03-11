import unittest
from tempfile import mkdtemp
outdir= mkdtemp(prefix='conversion_tests_')
from os.path import join as pjoin, dirname

TEST_DATA_DIR= pjoin(dirname(__file__), 'data')

REFERENCE_NRRD= pjoin(TEST_DATA_DIR, 'WIP_dti_ax_601.nhdr')

REFERENCE_NIFTI= pjoin(TEST_DATA_DIR, 'WIP_dti_ax_601.nii.gz')
REFERENCE_BVAL= pjoin(TEST_DATA_DIR, 'WIP_dti_ax_601.bval')
REFERENCE_BVEC= pjoin(TEST_DATA_DIR, 'WIP_dti_ax_601.bvec')

CONVERTED_NHDR= pjoin(TEST_DATA_DIR, 'CONVERTED_WIP_dti_ax_601.nhdr')

CONVERTED_NIFTI= pjoin(TEST_DATA_DIR, 'CONVERTED_WIP_dti_ax_601.nii.gz')
CONVERTED_BVAL= pjoin(TEST_DATA_DIR, 'CONVERTED_WIP_dti_ax_601.bval')
CONVERTED_BVEC= pjoin(TEST_DATA_DIR, 'CONVERTED_WIP_dti_ax_601.bvec')

REPEATED_NIFTI= pjoin(TEST_DATA_DIR, 'Repeated_WIP_dti_ax_601.nii.gz')
REPEATED_BVAL= pjoin(TEST_DATA_DIR, 'Repeated_WIP_dti_ax_601.bval')
REPEATED_BVEC= pjoin(TEST_DATA_DIR, 'Repeated_WIP_dti_ax_601.bvec')

REPEATED_NRRD= pjoin(TEST_DATA_DIR, 'Repeated_WIP_dti_ax_601.nhdr')

MULTI_NIFTI= pjoin(TEST_DATA_DIR, 'Multi_WIP_dti_ax_601.nii.gz')
MULTI_BVAL= pjoin(TEST_DATA_DIR, 'Multi_WIP_dti_ax_601.bval')
MULTI_BVEC= pjoin(TEST_DATA_DIR, 'Multi_WIP_dti_ax_601.bvec')

QC_FILE= pjoin(TEST_DATA_DIR, 'bad_index.txt')
BAD_INTERVAL= [100,600]