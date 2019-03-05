#/usr/bin/env python

import os
import numpy as np
try:
    labeFile= os.path.join(os.environ['FREESURFER_HOME'], 'FreeSurferColorLUT.txt')
except:
    raise KeyError('Set FREESURFER_HOME first and try again')

contents= open(labeFile).read()
lines= contents.split('\n')

def parse_labels(labels):

    dictionary={}
    names=[]
    for line in lines:
        for i, label in enumerate(labels):
            if line and '#' not in line:
                num, name= line.split()[:2]
                if int(num)== label:
                    dictionary[num]= name
                    names.append(name)
                    labels= np.delete(labels,i)

    # print(dictionary)
    return dictionary
    # return names

if __name__ == '__main__':
    parse_labels([10, 5, 100, 4, 3, 4, 100])