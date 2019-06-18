import numpy as np
PRECISION= 17
np.set_printoptions(precision= PRECISION, suppress= True, floatmode= 'maxprec')

def read_bvecs(bvec_file, assume_normed= True):

    with open(bvec_file, 'r') as f:
        bvecs = [[float(num) for num in line.split()] for line in f.read().split('\n') if line]

    # bvec_file can be 3xN or Nx3
    # we want to return as Nx3
    if len(bvecs) == 3:
        bvecs = transpose(bvecs)

    if not assume_normed:
        # normalize the bvecs
        for i in range(len(bvecs)):
            L_2 = np.linalg.norm(bvecs[i])
            if L_2:
                bvecs[i]/= L_2
            else:
                bvecs[i]= [0, 0, 0]

    return bvecs


def read_bvals(bval_file):

    with open(bval_file, 'r') as f:
        bvals = [float(num) for num in f.read().split()]

    # bval_file can be 1 line or N lines
    return bvals


def write_bvals(bval_file, bvals):
    with open(bval_file, 'w') as f:
        f.write(('\n').join(str(b) for b in bvals))


def write_bvecs(bvec_file, bvecs):
    with open(bvec_file, 'w') as f:
        # when bvecs is a list
        f.write(('\n').join((' ').join(str(i) for i in row) for row in bvecs))

        # when bvecs is a matrix
        # f.write(('\n').join((' ').join(str(i) for i in row.tolist()[0]) for row in bvecs))

        # if the above block prints [], use the following instead
        # with open(out_prefix+'.bvec', 'w') as f:
        #     for row in bvecs:
        #         f.write((' ').join(str(i) for i in row)+ '\n')


def transpose(bvecs):
    # bvecs_T = matrix(list(map(list, zip(*bvecs))))
    bvecs_T = list(map(list, zip(*bvecs)))

    return bvecs_T


def bvec_transpose(old_bvec_file, new_bvec_file):
    # read bvecs
    bvecs = read_bvecs(old_bvec_file)

    # making 3xN
    bvecs_T = transpose(bvecs)

    # write bvecs back
    write_bvecs(new_bvec_file, bvecs_T)


def tranpose(bvecs):

    # bvecs_T = matrix(list(map(list, zip(*bvecs))))
    bvecs_T = list(map(list, zip(*bvecs)))

    return bvecs_T


def bvec_rotate(old_bvec_file, new_bvec_file, rot_matrix):

    # read bvecs
    bvecs= read_bvecs(old_bvec_file)

    # making 3xN
    bvecs_T= tranpose(bvecs)

    # rotate bvecs
    bvecs_T= np.matrix.round(rot_matrix @ np.matrix(bvecs_T), PRECISION)

    # making Nx3 again
    bvecs = tranpose(bvecs_T)

    # write bvecs back
    write_bvecs(new_bvec_file, bvecs)


def bvec_scaling(bval, bvec, b_max):
    if bval:
        factor = np.sqrt(bval / b_max)
        if np.linalg.norm(bvec) != factor:
            bvec = np.array(bvec) * factor

    # bvec= [str(np.round(x, precision)) for x in bvec]
    bvec = [str(x) for x in bvec]

    return ('   ').join(bvec)

def read_grad_ind(filename):

    with open(filename) as f:
        content= f.read()

    indices= content.replace(',', ' ')
    indices= indices.split()

    if indices:
        return [int(x) for x in indices]
    else:
        raise IndexError('qc index list is empty')


def nrrd_bvals_bvecs(hdr):
    if hdr['dimension'] == 4:
        axis_elements = hdr['kinds']
    else:
        raise AttributeError('Not a valid dwi, check dimension')

    for i in range(4):
        if axis_elements[i] == 'list' or axis_elements[i] == 'vector':
            grad_axis = i
            break


    b_max = float(hdr['DWMRI_b-value'])

    N = hdr['sizes'][grad_axis]
    bvals = np.empty(N, dtype=float)
    bvecs = np.empty((N, 3), dtype=float)
    for ind in range(N):
        bvec = [float(num) for num in hdr[f'DWMRI_gradient_{ind:04}'].split()]
        L_2 = np.linalg.norm(bvec)
        bvals[ind] = round(L_2 ** 2 * b_max)

        if L_2:
            bvecs[ind] = bvec / L_2
        else:
            bvecs[ind] = [0, 0, 0]


    return (bvals, bvecs, b_max, grad_axis, N)

