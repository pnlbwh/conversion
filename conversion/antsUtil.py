from subprocess import check_call
from plumbum.cmd import antsApplyTransforms
from plumbum import FG

def antsReg(fixedImg, fixedMask, movingImg, outPrefix):
    if fixedMask:
        check_call((' ').join(['antsRegistrationSyNQuick.sh',
                               '-d', '3',
                               '-f', fixedImg,
                               '-x', fixedMask,
                               '-m', movingImg,
                               '-o', outPrefix]), shell=True)
    else:
        check_call((' ').join(['antsRegistrationSyNQuick.sh',
                               '-d', '3',
                               '-f', fixedImg,
                               '-m', movingImg,
                               '-o', outPrefix]), shell=True)


def applyXform(inImg, refImg, warp, trans, outImg, interp='Linear'):
    antsApplyTransforms[
        '-d', '3',
        '-i', inImg,
        '-o', outImg,
        '-r', refImg,
        '-t', warp, trans,
        '-n', interp,
    ] & FG
