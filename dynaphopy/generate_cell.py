import numpy as np

def generate_VASP_structure(structure, scaled=False, super_cell=(1, 1, 1)):

    cell = structure.get_cell(super_cell=super_cell)

    types = structure.get_atomic_types(super_cell=super_cell)
    atom_type_unique = np.unique(types, return_counts=True)

    elements = atom_type_unique[0]
    elements_count = atom_type_unique[1]

    vasp_POSCAR = 'Generated using dynaphopy\n'
    vasp_POSCAR += '1.0\n'
    for row in cell.T:
        vasp_POSCAR += '{0:20.10f} {1:20.10f} {2:20.10f}\n'.format(*row)
    vasp_POSCAR += ' '.join(elements)
    vasp_POSCAR += ' \n'
    vasp_POSCAR += ' '.join([str(i) for i in elements_count])

    if scaled:
        scaled_positions = structure.get_scaled_positions(super_cell=super_cell)
        vasp_POSCAR += '\nDirect\n'
        for row in scaled_positions:
            vasp_POSCAR += '{0:15.15f}   {1:15.15f}   {2:15.15f}\n'.format(*row)

    else:
        positions = structure.get_positions(super_cell=super_cell)
        vasp_POSCAR += '\nCartesian\n'
        for row in positions:
            vasp_POSCAR += '{0:20.10f} {1:20.10f} {2:20.10f}\n'.format(*row)

    return vasp_POSCAR


def generate_LAMMPS_structure(structure, super_cell=(1, 1, 1), by_element=True):

    cell = structure.get_cell(super_cell=super_cell)
    types = structure.get_atomic_types(super_cell=super_cell)

    if by_element:
        count_index_unique = np.unique(types, return_counts=True)[1]

        atom_index = []
        for i, index in enumerate(count_index_unique):
            atom_index += [i for j in range(index)]

    else:
        atom_index = structure.get_atom_type_index(super_cell=super_cell)

    atom_index_unique = np.unique(atom_index, return_index=True)[1]

    masses = structure.get_masses(super_cell=super_cell)

    positions = structure.get_positions(super_cell=super_cell)
    number_of_atoms = len(positions)


    lammps_data_file = 'Generated using dynaphopy\n\n'
    lammps_data_file += '{0} atoms\n\n'.format(number_of_atoms)

    lammps_data_file += '{0} atom types\n\n'.format(len(atom_index_unique))

    a, b, c, alpha, beta, gamma = structure.get_cell_parameters(super_cell=super_cell)

    xhi = a
    xy = b * np.cos(gamma)
    xz = c * np.cos(beta)
    yhi = np.sqrt(pow(b,2)- pow(xy,2))
    yz = (b*c*np.cos(alpha)-xy * xz)/yhi
    zhi = np.sqrt(pow(c,2)-pow(xz,2)-pow(yz,2))

    xhi = xhi + max(0,0, xy, xz, xy+xz)
    yhi = yhi + max(0,0, yz)

    lammps_data_file += '\n{0:20.10f} {1:20.10f} xlo xhi\n'.format(0, xhi)
    lammps_data_file += '{0:20.10f} {1:20.10f} ylo yhi\n'.format(0, yhi)
    lammps_data_file += '{0:20.10f} {1:20.10f} zlo zhi\n'.format(0, zhi)
    lammps_data_file += '{0:20.10f} {1:20.10f} {2:20.10f} xy xz yz\n\n'.format(xy, xz, yz)

    lammps_data_file += 'Masses\n\n'

    for i, index in enumerate(atom_index_unique):
        lammps_data_file += '{0} {1:20.10f} \n'.format(i+1, masses[index])

    lammps_data_file += '\nAtoms\n\n'
    for i, row in enumerate(positions):
        lammps_data_file += '{0} {1} {2:20.10f} {3:20.10f} {4:20.10f}\n'.format(i+1, atom_index[i]+1, row[0],row[1],row[2])

    return lammps_data_file

if __name__ == "__main__":

    import dynaphopy.interface.iofile as reading
    input_parameters = reading.read_parameters_from_input_file('/home/abel/VASP/Ag2Cu2O4/MD/input_dynaphopy')
    structure = reading.read_from_file_structure_poscar(input_parameters['structure_file_name_poscar'])
 #   print(generate_VASP_structure(structure))
    print(generate_LAMMPS_structure(structure))