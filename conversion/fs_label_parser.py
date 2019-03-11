#/usr/bin/env python

from numpy import delete
from os.path import join as pjoin, dirname

labelFile= pjoin(dirname(__file__),'data','FreeSurferColorLUT.txt')
contents= open(labelFile).read()
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
                    labels= delete(labels,i)

    # print(dictionary)
    return dictionary
    # return names

if __name__ == '__main__':
    parse_labels([10, 5, 100, 4, 3, 4, 100])