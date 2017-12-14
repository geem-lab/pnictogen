#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
from nose.tools import assert_equals
from numpy.testing import assert_allclose
from pnictogen.molecule import Molecule


def test_molecule_and_atom_from_smiles_string():
    mol = Molecule("c1ccccc1-c2ccccc2", "can")  # biphenyl
    oxygen = mol.atoms[0]

    assert_equals(oxygen.name, "Carbon")  # mendeleev
    assert_equals(oxygen.symbol, "C")  # mendeleev
    assert_equals(oxygen.vdw_radius, 170.)  # mendeleev
    assert_equals(oxygen.atomic_number, 6)


def test_molecule_and_atom_from_xyz_file():
    water = os.path.join(os.path.dirname(__file__), "../examples/water.xyz")

    with open(water) as w:
        mol = Molecule(w.read(), "xyz")

    for i, atom in enumerate(mol):
        assert_equals(mol.atoms[i].name, atom.name)  # mendeleev
        assert_equals(mol.atoms[i].symbol, atom.symbol)  # mendeleev
        assert_equals(mol.atoms[i].vdw_radius, atom.vdw_radius)  # mendeleev
        assert_equals(mol.atoms[i].atomic_number, atom.atomic_number)

    oxygen = mol.atoms[0]

    assert_allclose(oxygen.coords,
                    np.array([0.05840270608434, 0.05840270587342, 0.]))

    assert_equals(mol.spin, 1)
    assert_equals(mol.title, "PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2")
    assert_equals(mol.charge, 0)
    assert_equals(mol.write("can"), mol.write())  # openbabel

    mol.spin = 3
    mol.title = "Hello world!"
    mol.charge = -1

    assert_equals(mol.spin, 3)
    assert_equals(mol.title, "Hello world!")
    assert_equals(mol.charge, -1)
    assert_equals(mol.write("can"), "O\tHello world!\n")  # openbabel
    assert_equals(mol.write("xyz"), """3
Hello world!
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000
""")  # openbabel
    assert_equals(mol.write("mop"), """PUT KEYWORDS HERE
Hello world!

O   0.05840 1  0.05840 1  0.00000 1
H   1.00961 1 -0.06802 1  0.00000 1
H  -0.06802 1  1.00961 1  0.00000 1
""")  # openbabel


def test_molecule_and_atom_from_OBMol():
    mol = Molecule("N1CC2CCCC2CC1", "can")  # perhydroisoquinoline
    mol2 = Molecule(mol.OBMol)

    assert_equals(mol.spin, mol2.spin)
    assert_equals(mol.title, mol2.title)
    assert_equals(mol.charge, mol2.charge)

    for atom, atom2 in zip(mol, mol2):
        assert_allclose(atom.coords, atom2.coords)

        assert_equals(atom.name, atom2.name)  # mendeleev
        assert_equals(atom.symbol, atom2.symbol)  # mendeleev
        assert_equals(atom.vdw_radius, atom2.vdw_radius)  # mendeleev
        assert_equals(atom.atomic_number, atom2.atomic_number)


def test_molecule_write_can():
    mol = Molecule("OCC")

    assert_equals(mol.write("can"), "CCO\tCCO\n")
    assert_equals(mol.write("can"), mol.write())


def test_molecule_write_simplexyz():
    mol = Molecule("O")

    assert_equals(mol.write("simplexyz"),
                  "O          0.00000        0.00000        0.00000")

    with open("examples/water.xyz") as stream:
        mol = Molecule(stream.read(), "xyz")

    assert_equals(
        mol.write("simplexyz"),
        """O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000"""
    )


def test_molecule_write_simplemop():
    mol = Molecule("O")

    assert_equals(mol.write("simplemop"),
                  "O   0.00000 1  0.00000 1  0.00000 1")

    with open("examples/water.xyz") as stream:
        mol = Molecule(stream.read(), "xyz")

    assert_equals(
        mol.write("simplemop"),
        """O   0.05840 1  0.05840 1  0.00000 1
H   1.00961 1 -0.06802 1  0.00000 1
H  -0.06802 1  1.00961 1  0.00000 1"""
    )
