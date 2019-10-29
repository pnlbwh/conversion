from os.path import isfile
from distutils.spawn import find_executable

def read_imgs_masks(file):

    with open(file) as f:

        imgs = []
        masks = []
        content= f.read().strip()

        for line, row in enumerate(content.split('\n')):
            temp= [element.strip() for element in row.split(',') if element] # handling w/space

            if len(temp) != 2:
                raise FileNotFoundError(f'Columns don\'t have same number of entries: check line {line} in {file}')

            for img in temp:
                if not isfile(img):
                    raise FileNotFoundError(f'{img} does not exist: check line {line} in {file}')

            imgs.append(temp[0])
            masks.append(temp[1])


    return (imgs, masks)


def read_imgs(file):

    with open(file) as f:

        imgs = []
        content= f.read().strip()

        for line, row in enumerate(content.split('\n')):
            if row and not isfile(row): # handling w/space
                raise FileNotFoundError(f'{row} can\'t be found: check line {line} in {file}')
            else:
                imgs.append(row)

    return imgs


def read_cases(file):

    f = open(file, 'r')

    # omit any empty line in the caselist.txt
    subjects = []
    for s in list(f):
        temp = s.strip()
        if temp:
            subjects.append(temp)
    
    f.close()

    return subjects


def loadExecutable(exe):

    if find_executable(exe) is None:
        print(f'{exe} could not be found')
        print(f'Set "export PATH=$PATH:path_of_{exe}" and retry')
        exit(1)
    else:
        print(f'{exe} found')


def num2str(x):
    if x>10e-7:
        if x%1:
            return f'%.6f' % x
        else:
            return f'%d' % x
    else:
        return '0'

