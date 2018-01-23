#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cinfony import pybel
from nose.tools import assert_equals

from pnictogen.helpers import fragment, xyz

water_mol = pybel.readfile("xyz", "examples/water.xyz").next()
dimer_mol = pybel.readfile("xyz", "examples/water_dimer.xyz").next()


def test_fragment():
    assert_equals([xyz(frag) for frag in fragment(dimer_mol)],
                  ["""O          0.12908       -0.26336        0.64798
H          0.89795        0.28805        0.85518
H          0.10833       -0.20468       -0.33302""", """O          0.31020        0.07569       -2.07524
H         -0.26065        0.64232       -2.62218
H          0.64083       -0.57862       -2.71449"""])


def test_xyz():
    assert_equals(xyz(water_mol), xyz(water_mol, style="standard"))
    assert_equals(xyz(water_mol),
                  """O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000""")
    assert_equals(xyz(water_mol, style="MOPAC"),
                  """O   0.05840 1  0.05840 1  0.00000 1
H   1.00961 1 -0.06802 1  0.00000 1
H  -0.06802 1  1.00961 1  0.00000 1""")
