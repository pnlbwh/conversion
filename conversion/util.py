from os.path import isfile

def read_caselist(file):

    with open(file) as f:

        imgs = []
        masks = []
        content= f.read()
        for line, row in enumerate(content.split()):
            temp= [element for element in row.split(',') if element] # handling w/space

            if len(temp) != 2:
                raise FileNotFoundError(f'Columns don\'t have same number of entries: check line {line} in {file}')

            for img in temp:
                if not isfile(img):
                    raise FileNotFoundError(f'{img} does not exist: check line {line} in {file}')

            imgs.append(temp[0])
            masks.append(temp[1])


        return (imgs, masks)


def num2str(x):
    if x>10e-7:
        if x%1:
            return f'%.6f' % x
        else:
            return f'%d' % x
    else:
        return '0'