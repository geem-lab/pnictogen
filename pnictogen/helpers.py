#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: use mendeleev for periodic table
# TODO: allow the generation of conformers without energy evaluations
# TODO: simple interface to MOPAC
# TODO: make it easy to get number of electrons
# TODO: function zmat() similar to xyz()
# TODO: function rmsd(molecules) for calculating RMSD for a set of structures
# TODO: function fragment(molecule) for splitting a molecule


def xyz(molecule, style="standard"):
    """
    Get cartesian coordinates for molecule

    Parameters
    ----------
    molecule : pybel.Molecule
    style : str, optional
        Style of the cartesian coordinates. This can be "MOPAC" or "standard"
        at the moment.

    Returns
    -------
    str
        Molecular cartesian coordinates as string in the given style

    Examples
    --------
    >>> from cinfony import pybel
    >>> water_mol = pybel.readfile("xyz", "examples/water.xyz").next()
    >>> print(xyz(water_mol, style="MOPAC"))
    O   0.05840 1  0.05840 1  0.00000 1
    H   1.00961 1 -0.06802 1  0.00000 1
    H  -0.06802 1  1.00961 1  0.00000 1
    """

    if style == "standard":
        converted = molecule.write("xyz")
        converted = converted.split("\n", 2)[2].strip()
    elif style == "MOPAC":
        converted = molecule.write("mop")
        converted = converted.split("\n", 2)[2].strip()
    else:
        raise KeyError

    return converted


# This dict is set to globals prior to template renderization
available_helpers = {
    "xyz": xyz
}
