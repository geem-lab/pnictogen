#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: use mendeleev for periodic table
# TODO: maybe not here, but allow the generation of conformers without energy
# evaluations
# TODO: simple interface to MOPAC
# TODO: make it easy to get number of electrons


def coords(molecule, format="xyz"):
    """
    Write coordinates

    Parameters
    ----------
    molecule : pybel.Molecule
    format : str
        Format of the coordinates ("xyz" or "mop"). See example below.

    Returns
    -------
    str
        A string representing the molecular coordinates

    Examples
    --------
    A molecule can be written in a specified format:

    >>> from cinfony import pybel
    >>> mol = pybel.readfile("xyz", "examples/water.xyz").next()
    >>> print(coords(mol, "mop"))
    O   0.05840 1  0.05840 1  0.00000 1
    H   1.00961 1 -0.06802 1  0.00000 1
    H  -0.06802 1  1.00961 1  0.00000 1
    """
    converted = molecule.write(format)
    if format in {"xyz", "mop"}:
        converted = converted.split("\n", 2)[2].strip()
    else:
        raise KeyError
    return converted


# This dict is set to globals prior to template renderization
available_helpers = {
    "coords": coords
}
