#!/usr/bin/env python

import nrrd
from plumbum import cli

class App(cli.Application):

    force = cli.Flag(['--force'], help='Force overwrite if output already exists',mandatory=False,default=False)

    nrrdFile = cli.SwitchAttr(
        ['-i', '--input'],
        cli.ExistingFile,
        help='input nrrd',
        mandatory=True)

    nhdrFile = cli.SwitchAttr(
        ['-o', '--out'],
        cli.NonexistentPath,
        help='output nhdr',
        mandatory=True)

    def main(self):

        img= nrrd.read(self.nrrdFile)

        nrrd.write(self.nhdrFile, img[0], header=img[1], compression_level = 1)


if __name__ == '__main__':
    App.run()