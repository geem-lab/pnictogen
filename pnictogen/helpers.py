#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pybel
import numpy as np

# TODO: use mendeleev for periodic table
# TODO: simple interface to MOPAC
# TODO: make it easy to get number of electrons
# TODO: function zmat() similar to xyz()
# TODO: function rmsd(molecules) for calculating RMSD for a set of structures


# TODO: fix bonds between specific atoms or all bonds of a specific atom
def conformers(molecule, nconf=30, children=5, mutability=5, convergence=25,
               copyformat="xyz"):
    """
    Conformer search provided by Open Babel based on a genetic algorithm.
    You might want to play around with the parameters for this function (see
    below).

    Parameters
    ----------
    molecule : pybel.Molecule
        The molecule with initial conformer
    nconf : int, optional
        Maximum number of conformers that should be generated. This is also the
        number of conformers selected for each generation.
    children : int, optional
        When a new generation is generated, for each of the nconf conformers,
        this number of children are created.
    mutability : int, optional
        This determines how frequent a permutation occurs when generating the
        next generation (e.g. 5 means 1/5 bonds are permuted, 10 means 1/10,
        etc.).
    convergence : int, optional
        The number of identical generations before considering the process
        converged.
    copyformat : str, optional
        File format to be used internally

    Returns
    -------
    list of pybel.Molecule

    Examples
    --------
    The number of conformers found will depend on the number of rotatable
    bonds in the molecule:

    >>> for i in range(1, 8):
    ...     smi = "C" * i
    ...     mol = pybel.readstring("smi", smi)
    ...     nconf = len(conformers(mol))
    ...     print("Found {:2d} conformers for {:s}".format(nconf, smi))
    Found  1 conformers for C
    Found  1 conformers for CC
    Found  1 conformers for CCC
    Found  3 conformers for CCCC
    Found  7 conformers for CCCCC
    Found 17 conformers for CCCCCC
    Found 30 conformers for CCCCCCC
    """

    num_rotors = molecule.OBMol.NumRotors()
    if num_rotors < 1:
        # Nothing to rotate
        return [molecule]

    if molecule.dim < 3:
        molecule.make3D()

    copy_molecule = pybel.readstring(copyformat, molecule.write(copyformat))

    cs = pybel.ob.OBConformerSearch()
    cs.Setup(copy_molecule.OBMol, nconf, children, mutability, convergence)

    cs.Search()
    cs.GetConformers(copy_molecule.OBMol)

    conformers = []
    for i in range(copy_molecule.OBMol.NumConformers()):
        copy_molecule.OBMol.SetConformer(i)
        conformers.append(pybel.readstring(copyformat,
                                           copy_molecule.write(copyformat)))
    return conformers


def fragment(molecule, indices=None):
    """
    Split molecule into fragments

    If indices is not given, atoms might permute in fragments, when compared to
    the original order (<https://github.com/openbabel/openbabel/issues/1763>).

    Parameters
    ----------
    molecule : pybel.Molecule
    indices : list of tuples of int, optional
        Assigments of atoms to fragments. Each element of indices is a tuple
        with atomic indices representing a fragment (see examples below).

    Returns
    -------
    list of pybel.Molecule

    Examples
    --------
    By default, fragment simply returns all non-bonded fragments:

    >>> dimer_mol = list(pybel.readfile("xyz", "examples/water_dimer.xyz"))[0]
    >>> for water_mol in fragment(dimer_mol):
    ...     print(water_mol.write("xyz"))
    3
    <BLANKLINE>
    O          0.12908       -0.26336        0.64798
    H          0.89795        0.28805        0.85518
    H          0.10833       -0.20468       -0.33302
    <BLANKLINE>
    3
    <BLANKLINE>
    O          0.31020        0.07569       -2.07524
    H         -0.26065        0.64232       -2.62218
    H          0.64083       -0.57862       -2.71449
    <BLANKLINE>

    But if indices are given, fragments are built from the corresponding
    atoms. This allows one to perform extraction and permutation of atoms:

    >>> for water_mol in fragment(dimer_mol, [(4, 5, 3), (1, 0)]):
    ...     print(water_mol.write("xyz"))
    3
    <BLANKLINE>
    H          0.64083       -0.57862       -2.71449
    H         -0.26065        0.64232       -2.62218
    O          0.31020        0.07569       -2.07524
    <BLANKLINE>
    2
    <BLANKLINE>
    H          0.89795        0.28805        0.85518
    O          0.12908       -0.26336        0.64798
    <BLANKLINE>
    """
    if indices is not None:
        fragments = []
        for atom_ids in indices:
            fragment_obmol = pybel.ob.OBMol()
            for i in atom_ids:
                obatom = molecule.OBMol.GetAtomById(i)
                fragment_obmol.InsertAtom(obatom)

            fragments.append(pybel.Molecule(fragment_obmol))
        return fragments

    return [pybel.Molecule(frag) for frag in molecule.OBMol.Separate()]


def xyz(molecule, style="standard", flag=None, fixed_atoms=None):
    """
    Get cartesian coordinates for molecule

    Parameters
    ----------
    molecule : pybel.Molecule
    style : str, optional
        Dialect of cartesian coordinates. This can be "ADF", "GAMESS", "MOPAC",
        "ORCA" or "standard".
    flag : str, optional
        If style is "ADF", an extra column is added for naming this fragment
        (see examples below).
    fixed_atoms : iterable object of int
        If style is "MOPAC", the extra columns in output will change in order
        to fix the cartesian coordinates of listed atoms.

    Returns
    -------
    converted : str
        Molecular cartesian coordinates as string in the given style

    Examples
    --------
    >>> water_mol = list(pybel.readfile("xyz", "examples/water.xyz"))[0]
    >>> print(xyz(water_mol, style="MOPAC"))
    O   0.05840 1  0.05840 1  0.00000 1
    H   1.00961 1 -0.06802 1  0.00000 1
    H  -0.06802 1  1.00961 1  0.00000 1

    >>> print(xyz(water_mol, style="GAMESS"))
    O      8.0      0.0584027061    0.0584027059    0.0000000000
    H      1.0      1.0096135406   -0.0680162466    0.0000000000
    H      1.0     -0.0680162466    1.0096135407    0.0000000000

    Fragment naming in ADF can be given:

    >>> print(xyz(water_mol, style="ADF", flag="frag1"))
    O          0.05840        0.05840        0.00000       f=frag1
    H          1.00961       -0.06802        0.00000       f=frag1
    H         -0.06802        1.00961        0.00000       f=frag1
    """

    if style in {"ADF", "ORCA", "standard"}:
        converted = molecule.write("xyz")
        converted = converted.split("\n", 2)[2].strip()

        if flag is not None:
            if style == "ADF":
                converted = "\n".join(["{}       f={}".format(line, flag)
                                       for line in converted.split("\n")])
            elif style == "ORCA":
                flag = "({})".format(flag)
                converted = "\n".join([line.replace(" " * len(flag), flag, 1)
                                      for line in converted.split("\n")])
            else:
                raise KeyError
    elif style == "GAMESS":
        converted = molecule.write("gamin").strip()
        converted = converted.split("\n")[5:-1]
        converted = "\n".join([line.strip() for line in converted])
    elif style == "MOPAC":
        converted = molecule.write("mop")
        converted = converted.split("\n", 2)[2].strip()
        if fixed_atoms is not None:
            converted = converted.split("\n")
            for i in fixed_atoms:
                converted[i] = re.sub(' 1( |$)', ' 0\g<1>', converted[i])
            converted = "\n".join(converted)
    else:
        raise KeyError

    return converted


# This dict is set to globals prior to template renderization
available_helpers = {
    "conformers": conformers,
    "fragment": fragment,
    "np": np,
    "xyz": xyz,
}
