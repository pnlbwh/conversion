import os
import sys

# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from numpy import testing
from conversion.tests.util import *
from nrrd import read
from nibabel import load
import conversion
import shutil

class TestFileConversion(unittest.TestCase):

    def test_nrrd2nifti(self):

        PREFIX= pjoin(outdir, 'nrrd2nifti_prefix')

        # run nrrd2nifti conversion
        conversion.nifti_write(REFERENCE_NRRD, PREFIX)

        # load converted output
        converted_nifti= load(PREFIX+'.nii.gz')
        converted_nifti_data= converted_nifti.get_data()
        converted_nifti_affine= converted_nifti.affine
        converted_nifti_bvals= conversion.read_bvals(PREFIX+'.bval')
        converted_nifti_bvecs = conversion.read_bvecs(PREFIX+'.bvec')

        # load converted reference
        converted_nifti= load(CONVERTED_NIFTI)
        reference_nifti_data= converted_nifti.get_data()
        reference_nifti_affine= converted_nifti.affine
        reference_nifti_bvals= conversion.read_bvals(CONVERTED_BVAL)
        reference_nifti_bvecs = conversion.read_bvecs(CONVERTED_BVEC)

        # test equality
        testing.assert_array_equal(reference_nifti_data, converted_nifti_data)
        testing.assert_array_equal(reference_nifti_affine, converted_nifti_affine)
        testing.assert_array_equal(reference_nifti_bvals, converted_nifti_bvals)
        testing.assert_array_equal(reference_nifti_bvecs, converted_nifti_bvecs)


    def test_nifti2nrrd(self):

        PREFIX= pjoin(outdir, 'nifti2nhdr')

        # run nifti2nrrd conversion
        conversion.nhdr_write(REFERENCE_NIFTI, REFERENCE_BVAL, REFERENCE_BVEC, PREFIX+'.nhdr')
        shutil.copy(REFERENCE_NIFTI, pjoin(outdir, os.path.basename(REFERENCE_NIFTI)))

        # load converted output
        converted_nrrd_data, converted_nrrd_hdr = read(PREFIX+'.nhdr')
        converted_nrrd_bvals, converted_nrrd_bvecs = conversion.nrrd_bvals_bvecs(converted_nrrd_hdr)[:2]

        # load converted reference
        reference_nrrd_data, reference_nrrd_hdr = read(CONVERTED_NHDR)
        reference_nrrd_bvals, reference_nrrd_bvecs = conversion.nrrd_bvals_bvecs(reference_nrrd_hdr)[:2]

        # test equality
        testing.assert_equal(reference_nrrd_hdr, converted_nrrd_hdr)
        testing.assert_array_equal(reference_nrrd_data, converted_nrrd_data)
        testing.assert_array_equal(reference_nrrd_bvals, converted_nrrd_bvals)
        testing.assert_array_equal(reference_nrrd_bvecs, converted_nrrd_bvecs)


if __name__ == '__main__':
    unittest.main()