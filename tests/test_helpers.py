#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pybel
from nose.tools import assert_equals

from pnictogen import main
from pnictogen.helpers import conformers, fragment, xyz

water_mol = list(pybel.readfile("xyz", "examples/water.xyz"))[0]
dimer_mol = list(pybel.readfile("xyz", "examples/water_dimer.xyz"))[0]
cyclohexanol_mol = list(pybel.readfile("xyz", "examples/cyclohexanol.xyz"))[0]
pentane_mol = list(pybel.readfile("xyz", "examples/pentane.xyz"))[0]


def test_conformers():
    cyclohexanol_conformers = conformers(cyclohexanol_mol)
    assert_equals(len(cyclohexanol_conformers), 1)

    pentane_conformers = conformers(pentane_mol)
    assert_equals(len(pentane_conformers), 7)

    output = pybel.Outputfile("xyz", "examples/pentane_conformers.xyz",
                              overwrite=True)
    for mol in pentane_conformers:
        output.write(mol)
    output.close()
    main(["examples/templates/opt.MOPAC.mop",
          "examples/pentane_conformers.xyz"])


def test_fragment():
    assert_equals([xyz(frag) for frag in fragment(dimer_mol)],
                  ["""O          0.12908       -0.26336        0.64798
H          0.89795        0.28805        0.85518
H          0.10833       -0.20468       -0.33302""", """O          0.31020        0.07569       -2.07524
H         -0.26065        0.64232       -2.62218
H          0.64083       -0.57862       -2.71449"""])

    assert_equals([xyz(frag) for frag in fragment(dimer_mol, [range(6)])],
                  [xyz(dimer_mol)])

    assert_equals([xyz(frag) for frag in fragment(dimer_mol, [(2, 1), (5,)])],
                  ["""H          0.10833       -0.20468       -0.33302
H          0.89795        0.28805        0.85518""",
                   "H         -0.26065        0.64232       -2.62218"])


def test_xyz():
    assert_equals(xyz(water_mol), xyz(water_mol, style="standard"))
    assert_equals(xyz(water_mol),
                  """O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000""")

    assert_equals(xyz(water_mol), xyz(water_mol, style="ADF"))
    assert_equals(xyz(water_mol, style="ADF", flag="water"),
                  """O          0.05840        0.05840        0.00000       f=water
H          1.00961       -0.06802        0.00000       f=water
H         -0.06802        1.00961        0.00000       f=water""")

    assert_equals(xyz(water_mol, style="GAMESS"),
                  """O      8.0      0.0584027061    0.0584027059    0.0000000000
H      1.0      1.0096135406   -0.0680162466    0.0000000000
H      1.0     -0.0680162466    1.0096135407    0.0000000000""")

    assert_equals(xyz(water_mol, style="MOPAC"),
                  """O   0.05840 1  0.05840 1  0.00000 1
H   1.00961 1 -0.06802 1  0.00000 1
H  -0.06802 1  1.00961 1  0.00000 1""")

    assert_equals(xyz(water_mol, style="MOPAC", fixed_atoms=[0, 2]),
                  """O   0.05840 0  0.05840 0  0.00000 0
H   1.00961 1 -0.06802 1  0.00000 1
H  -0.06802 0  1.00961 0  0.00000 0""")

    assert_equals(xyz(water_mol, style="MOPAC", fixed_atoms=[1]),
                  """O   0.05840 1  0.05840 1  0.00000 1
H   1.00961 0 -0.06802 0  0.00000 0
H  -0.06802 1  1.00961 1  0.00000 1""")
