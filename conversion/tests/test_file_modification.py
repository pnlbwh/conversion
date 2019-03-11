import os
import sys

# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from numpy import testing
from conversion.tests.util import *
from nrrd import read
from nibabel import load
import conversion


class TestFileConversion(unittest.TestCase):

    def setUp(self):
        self.ind = conversion.read_grad_ind(QC_FILE)

    def test_grad_remove_nifti_bad_index(self):
        conversion.grad_remove(MULTI_NIFTI, pjoin(outdir, 'nifti_remove_ind.nii.gz'), qc_bad_indices= self.ind,
                                bvalFile= MULTI_BVAL, bvecFile= MULTI_BVEC,)

    def test_grad_remove_nifti_bad_interval(self):
        conversion.grad_remove(MULTI_NIFTI, pjoin(outdir, 'nifti_remove_interval.nii.gz'), interval=BAD_INTERVAL,
                               bvalFile=MULTI_BVAL, bvecFile=MULTI_BVEC, )


    def test_grad_avg_nifti(self):
        conversion.grad_avg(REPEATED_NIFTI, pjoin(outdir, 'nifti_avg.nii.gz'), REPEATED_BVAL,
                            REPEATED_BVEC)

    def test_grad_avg_nrrd(self):
        conversion.grad_avg(REPEATED_NRRD, pjoin(outdir, 'nrrd_avg.nrrd'))


if __name__ == '__main__':
    unittest.main()