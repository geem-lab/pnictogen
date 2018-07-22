#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pybel

# TODO: use mendeleev for periodic table
# TODO: allow the generation of conformers without energy evaluations
# TODO: simple interface to MOPAC
# TODO: make it easy to get number of electrons
# TODO: function zmat() similar to xyz()
# TODO: function rmsd(molecules) for calculating RMSD for a set of structures


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


def xyz(molecule, style="standard", flag=None):
    """
    Get cartesian coordinates for molecule

    Parameters
    ----------
    molecule : pybel.Molecule
    style : str, optional
        Dialect of cartesian coordinates. This can be "MOPAC", "ADF" or
        "standard" at the moment.
    flag : str, optional
        If style is "ADF", an extra column is added for naming this fragment
        (see examples below).

    Returns
    -------
    str
        Molecular cartesian coordinates as string in the given style

    Examples
    --------
    >>> water_mol = list(pybel.readfile("xyz", "examples/water.xyz"))[0]
    >>> print(xyz(water_mol, style="MOPAC"))
    O   0.05840 1  0.05840 1  0.00000 1
    H   1.00961 1 -0.06802 1  0.00000 1
    H  -0.06802 1  1.00961 1  0.00000 1

    Fragment naming in ADF can be given:

    >>> print(xyz(water_mol, style="ADF", flag="frag1"))
    O          0.05840        0.05840        0.00000       f=frag1
    H          1.00961       -0.06802        0.00000       f=frag1
    H         -0.06802        1.00961        0.00000       f=frag1
    """

    if style in {"ADF", "standard"}:
        converted = molecule.write("xyz")
        converted = converted.split("\n", 2)[2].strip()

        if flag is not None:
            if style == "ADF":
                converted = "\n".join(["{}       f={}".format(line, flag)
                                       for line in converted.split("\n")])
            else:
                raise KeyError
    elif style == "MOPAC":
        converted = molecule.write("mop")
        converted = converted.split("\n", 2)[2].strip()
    else:
        raise KeyError

    return converted


# This dict is set to globals prior to template renderization
available_helpers = {
    "fragment": fragment,
    "xyz": xyz,
}
