#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for pnictogen module."""

import os
from glob import iglob

from pyrrole import atoms
from nose.tools import assert_equals
from contextlib import contextmanager

from pnictogen import argparser, main, pnictogen

# Only testing xyz files because I trust Open Babel to handle other file types
example_xyz_files = iglob("data/*.xyz")

templates = iglob("pnictogen/repo/*")


@contextmanager
def cd(newdir):
    """Change working directory."""
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def test_argparser():
    """Test if argparser works."""
    for template in templates:
        argv = [template] + list(example_xyz_files)

        parser = argparser()
        parser.parse_args(argv)


def test_main():
    """Test if main works."""
    for template in templates:
        main(["-g", template])

        # One at a time
        for xyz_file in example_xyz_files:
            main([template, xyz_file])

        # All at once
        main([template] + list(example_xyz_files))

    # Allow use of template in the parent directory
    with cd("data"):
        main(["../pnictogen/repo/split.ADF.in", "water-dimer.xyz"])


def test_pnictogen():
    """Test if pnictogen works."""
    for template in templates:
        template_prefix, extension = os.path.splitext(template)
        for xyz_file in example_xyz_files:
            input_prefix, xyz_file_extension = os.path.splitext(xyz_file)

            mol = atoms.read_pybel(xyz_file)
            written_files = pnictogen(mol, input_prefix, template,
                                      extension[1:])

            assert_equals(type(written_files), list)
            for written_file in written_files:
                assert_equals(type(written_file), str)

            written_files2 = pnictogen(mol, input_prefix, template)
            assert_equals(written_files, written_files2)

    # Allow use of template in the parent directory
    with cd("pnictogen/repo"):
        mol = atoms.read_pybel("../../data/water-dimer.xyz")
        written_files = pnictogen(mol, "../../data/water-dimer",
                                  "split.ADF.in", "in")

        assert_equals(written_files, ["../../data/water-dimer_eda.in",
                                      "../../data/water-dimer_f1.in",
                                      "../../data/water-dimer_f2.in"])

    main(["-g", "/tmp/hello.world.ORCA.inp"])
    mol = atoms.read_pybel("data/co.xyz")
    written_files = pnictogen(mol, "data/co",
                              "/tmp/hello.world.ORCA.inp", foo="bar")

    assert_equals(written_files, ["data/co.inp"])


def test_render_templates():
    """Test if templates are correctly rendered."""
    water_mol = atoms.read_pybel("data/water.xyz")

    main(["-g", "/tmp/foo.ADF.in"])
    main(["/tmp/foo.ADF.in", "data/water.xyz"])
    assert_equals(open("data/water.in").read().strip(),
                  water_mol.to_string("adf"))

    main(["-g", "/tmp/test.GAMESS.inp"])
    main(["/tmp/test.GAMESS.inp", "data/water.xyz"])
    assert_equals(open("data/water.inp").read(),
                  """ $CONTRL COORD=CART UNITS=ANGS $END

 $DATA
data/water.xyz
C1
O      8.0      0.0584027061    0.0584027059    0.0000000000
H      1.0      1.0096135406   -0.0680162466    0.0000000000
H      1.0     -0.0680162466    1.0096135407    0.0000000000
 $END


""")

    main(["-g", "/tmp/hello.GAMESSUK.inp"])
    main(["/tmp/hello.GAMESSUK.inp", "data/water.xyz"])
    assert_equals(open("data/water.inp").read(),
                  water_mol.to_string("gukin"))

    main(["-g", "/tmp/hello.world.Gaussian.gjf"])
    main(["/tmp/hello.world.Gaussian.gjf", "data/water.xyz"])
    assert_equals(open("data/water.gjf").read(),
                  """#Put Keywords Here, check Charge and Multiplicity.

 data/water.xyz

0  1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000

""")

    main(["-g", "/tmp/bar.Jaguar.in"])
    main(["/tmp/bar.Jaguar.in", "data/water.xyz"])
    assert_equals(open("data/water.in").read(), water_mol.to_string("jin"))

    main(["-g", "/tmp/foo.Molpro.inp"])
    main(["/tmp/foo.Molpro.inp", "data/water.xyz"])
    assert_equals(open("data/water.inp").read(), water_mol.to_string("mp"))

    main(["-g", "/tmp/example.MOPAC.mop"])
    main(["/tmp/example.MOPAC.mop", "data/water.xyz"])
    assert_equals(open("data/water.mop").read(),
                  """CHARGE=0 MS=0.0
data/water.xyz

O   0.05840 1  0.05840 1  0.00000 1
H   1.00961 1 -0.06802 1  0.00000 1
H  -0.06802 1  1.00961 1  0.00000 1
""")

    main(["-g", "/tmp/bar.MPQC.in"])
    main(["/tmp/bar.MPQC.in", "data/water.xyz"])
    assert_equals(open("data/water.in").read(),
                  water_mol.to_string("mpqcin"))

    main(["-g", "/tmp/foo.NWChem.nw"])
    main(["/tmp/foo.NWChem.nw", "data/water.xyz"])
    assert_equals(open("data/water.nw").read(), """start molecule

title data/water.xyz

geometry units angstroms print xyz autosym
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000
end
""")

    main(["-g", "/tmp/example.ORCA.inp"])
    main(["/tmp/example.ORCA.inp", "data/water.xyz"])
    assert_equals(open("data/water.inp").read(),
                  """# data/water.xyz
! Opt

* xyz 0 1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000
*
""")

    main(["-g", "/tmp/bar.Psi.dat"])
    main(["/tmp/bar.Psi.dat", "data/water.xyz"])
    assert_equals(open("data/water.dat").read(),
                  """# data/water.xyz

molecule {
0 1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000
units angstrom
}

optimize('scf')""")

    main(["-g", "/tmp/example.QChem.in"])
    main(["/tmp/example.QChem.in", "data/water.xyz"])
    assert_equals(open("data/water.in").read(),
                  water_mol.to_string("qcin"))

    main(["-g", "/tmp/foo.ZINDO.input"])
    main(["/tmp/foo.ZINDO.input", "data/water.xyz"])
    assert_equals(open("data/water.input").read(),
                  water_mol.to_string("zin"))


def test_example_eda_adf():
    """Test example for EDA in ADF."""
    main(["pnictogen/repo/split.ADF.in", "data/water-dimer.xyz"])
    assert_equals(open("data/water-dimer_eda.in").read(),
                  """TITLE data/water-dimer.xyz eda

CHARGE 0  0

Number of atoms
 6

ATOMS Cartesian
O          0.12908       -0.26336        0.64798       f=f1
H          0.89795        0.28805        0.85518       f=f1
H          0.10833       -0.20468       -0.33302       f=f1
O          0.31020        0.07569       -2.07524       f=f2
H         -0.26065        0.64232       -2.62218       f=f2
H          0.64083       -0.57862       -2.71449       f=f2
End

Fragments
 f1 data/water-dimer_f1.t21
 f2 data/water-dimer_f2.t21
End

Basis
End

Geometry
End

""")
    assert_equals(open("data/water-dimer_f1.in").read(),
                  """TITLE data/water-dimer.xyz f1

CHARGE 0  0

Number of atoms
 3

ATOMS Cartesian
O          0.12908       -0.26336        0.64798
H          0.89795        0.28805        0.85518
H          0.10833       -0.20468       -0.33302
End

Basis
End

Geometry
End

""")
    assert_equals(open("data/water-dimer_f2.in").read(),
                  """TITLE data/water-dimer.xyz f2

CHARGE 0  0

Number of atoms
 3

ATOMS Cartesian
O          0.31020        0.07569       -2.07524
H         -0.26065        0.64232       -2.62218
H          0.64083       -0.57862       -2.71449
End

Basis
End

Geometry
End

""")


def test_example_fragments_orca():
    """Test if fragmentation works with ORCA inputs."""
    main(["pnictogen/repo/split.ORCA.inp", "data/water-dimer.xyz"])
    assert_equals(open("data/water-dimer.inp").read(),
                  """# data/water-dimer.xyz
! Opt

* xyz 0 1
O(1)       0.12908       -0.26336        0.64798
H(1)       0.89795        0.28805        0.85518
H(1)       0.10833       -0.20468       -0.33302
O(2)       0.31020        0.07569       -2.07524
H(2)      -0.26065        0.64232       -2.62218
H(2)       0.64083       -0.57862       -2.71449
*""")


def test_read_with_cclib():
    """Test if we can correctly read with cclib through pyrrole."""
    main(["-g", "/tmp/fnord.Gaussian.gjf"])
    main(["/tmp/fnord.Gaussian.gjf", "data/benzene.out"])
    assert_equals(open("data/benzene.gjf").read(),
                  """#Put Keywords Here, check Charge and Multiplicity.

 data/benzene.out

0  1
C          1.74589        1.79575       -1.05975
C          0.94841        2.86897       -1.43112
C          1.44805        1.07435        0.08765
C         -0.14707        3.22061       -0.65525
C          0.35257        1.42599        0.86352
C         -0.44491        2.49921        0.49216
H          2.59974        1.52031       -1.66517
H          1.18103        3.43114       -2.32624
H          2.07000        0.23754        0.37812
H         -0.76902        4.05742       -0.94571
H          0.11995        0.86382        1.75864
H         -1.29876        2.77465        1.09757

""")
