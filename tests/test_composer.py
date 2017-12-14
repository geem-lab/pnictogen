#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import assert_equals
from pnictogen.molecule import Molecule
from pnictogen.composer import render_template

mol_salt = Molecule("[Na+].[Cl-] Salt")
mol_so = Molecule("SO")


def test_render_template():
    assert_equals(render_template("Hello world!"), "Hello world!")
    assert_equals(render_template(template="Hello {{ there }}!",
                                  context={"there": "world"}),
                  "Hello world!")


def test_render_template_with_element():
    assert_equals(render_template("{{ element('Pt').name }}"), "Platinum")
    assert_equals(render_template("{{ element('Pt').symbol }}"), "Pt")
    assert_equals(render_template("{{ element('Pt').vdw_radius }}"), "213.0")
    assert_equals(render_template("{{ element('Pt').atomic_number }}"), "78")


def test_compose_for_ADF():
    assert_equals(render_template(
        template="{% extends 'examples/templates/ADF.in' %}",
        context={"molecules": [mol_salt]}
    ), """TITLE Salt

CHARGE 0  1

Number of atoms
 2

ATOMS Cartesian
Na         0.00000        0.00000        0.00000
Cl         0.00000        0.00000        0.00000
End

Basis
End

Geometry
End


""")

    assert_equals(render_template(
        template="{% extends 'examples/templates/ADF.in' %}",
        context={"molecules": [mol_so]}
    ), """TITLE OS

CHARGE 0  1

Number of atoms
 2

ATOMS Cartesian
S          0.00000        0.00000        0.00000
O          0.00000        0.00000        0.00000
End

Basis
End

Geometry
End


""")


def test_compose_for_Gaussian():
    assert_equals(render_template(
        template="{% extends 'examples/templates/Gaussian.gjf' %}",
        context={"molecules": [mol_salt]}
    ), """#Put Keywords Here, check Charge and Multiplicity.

 Salt

0  1
Na         0.00000        0.00000        0.00000
Cl         0.00000        0.00000        0.00000

""")

    assert_equals(render_template(
        template="{% extends 'examples/templates/Gaussian.gjf' %}",
        context={"molecules": [mol_so]}
    ), """#Put Keywords Here, check Charge and Multiplicity.

 OS

0  1
S          0.00000        0.00000        0.00000
O          0.00000        0.00000        0.00000

""")


def test_compose_for_MOPAC():
    assert_equals(render_template(
        template="{% extends 'examples/templates/MOPAC.mop' %}",
        context={"molecules": [mol_salt]}
    ), """CHARGE=0 MS=0.0
Salt

Na  0.00000 1  0.00000 1  0.00000 1
Cl  0.00000 1  0.00000 1  0.00000 1

""")

    assert_equals(render_template(
        template="{% extends 'examples/templates/MOPAC.mop' %}",
        context={"molecules": [mol_so]}
    ), """CHARGE=0 MS=0.0
OS

S   0.00000 1  0.00000 1  0.00000 1
O   0.00000 1  0.00000 1  0.00000 1

""")


def test_compose_for_ORCA():
    assert_equals(render_template(
        template="{% extends 'examples/templates/ORCA.inp' %}",
        context={"molecules": [mol_salt]}
    ), """# Salt
! Opt

* xyz 0 1
Na         0.00000        0.00000        0.00000
Cl         0.00000        0.00000        0.00000
*
""")

    assert_equals(render_template(
        template="{% extends 'examples/templates/ORCA.inp' %}",
        context={"molecules": [mol_so]}
    ), """# OS
! Opt

* xyz 0 1
S          0.00000        0.00000        0.00000
O          0.00000        0.00000        0.00000
*
""")
