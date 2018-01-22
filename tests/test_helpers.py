#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cinfony import pybel
from nose.tools import assert_equals

from pnictogen.helpers import xyz

water_mol = pybel.readfile("xyz", "examples/water.xyz").next()


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
