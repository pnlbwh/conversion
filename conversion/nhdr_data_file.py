#!/usr/bin/env python

import os, sys
import fileinput
import argparse

def main():

    parser = argparse.ArgumentParser(description= 'nhdr data file path fixing')
    parser.add_argument('-i', '--input', type=str, required=True, help='input nhdr header')

    args = parser.parse_args()
    for line in fileinput.input(args.input, inplace= True):
        if ('data file' in line) or ('datafile' in line):
           datafile= line.split()[-1]
           datafile= os.path.basename(datafile)
           line= f'data file: {datafile}\n'

        # print appends extra newline
        # print(line)

        # use the following instead
        sys.stdout.write(line)

if __name__=='__main__':
    main()