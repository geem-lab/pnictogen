#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests for pnictogen module."""

import os
from glob import iglob
from contextlib import contextmanager

import cclib
from nose.tools import assert_equals
from pnictogen import Atoms, argparser, main, pnictogen

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
        main(["../pnictogen/repo/ADF.in", "water-dimer.xyz"])


def test_pnictogen():
    """Test if pnictogen works."""
    for template in templates:
        template_prefix, extension = os.path.splitext(template)
        for xyz_file in example_xyz_files:
            input_prefix, xyz_file_extension = os.path.splitext(xyz_file)

            mol = Atoms(
                cclib.bridge.cclib2openbabel.readfile(xyz_file, xyz_file_extension[1:])
            )
            written_files = pnictogen(mol, input_prefix, template, extension[1:])

            assert_equals(type(written_files), list)
            for written_file in written_files:
                assert_equals(type(written_file), str)

            written_files2 = pnictogen(mol, input_prefix, template)
            assert_equals(written_files, written_files2)

    # Allow use of template in the parent directory
    with cd("pnictogen/repo"):
        mol = Atoms(
            cclib.bridge.cclib2openbabel.readfile("../../data/water-dimer.xyz", "xyz")
        )
        written_files = pnictogen(mol, "../../data/water-dimer", "ADF.in", "in")

        assert_equals(
            written_files,
            [
                "../../data/water-dimer.in",
            ],
        )

    main(["-g", "/tmp/hello.world.ORCA.inp"])
    mol = Atoms(cclib.bridge.cclib2openbabel.readfile("data/co.xyz", "xyz"))
    written_files = pnictogen(mol, "data/co", "/tmp/hello.world.ORCA.inp", foo="bar")

    assert_equals(written_files, ["data/co.inp"])


def test_render_templates():
    """Test if templates are correctly rendered."""
    water_mol = Atoms(cclib.bridge.cclib2openbabel.readfile("data/water.xyz", "xyz"))
    if not water_mol.name:
        water_mol.name = "data/water.xyz"

    main(["-g", "/tmp/foo.ADF.in"])
    main(["/tmp/foo.ADF.in", "data/water.xyz"])
    assert_equals(
        open("data/water.in").read().strip(),
        """TITLE data/water.xyz

CHARGE 0  0

Number of atoms
 3

ATOMS Cartesian
O          0.0584027061        0.0584027059        0.0000000000
H          1.0096135406       -0.0680162466        0.0000000000
H         -0.0680162466        1.0096135407        0.0000000000
End

Basis
End

Geometry
End""",
    )

    main(["-g", "/tmp/test.GAMESS.inp"])
    main(["/tmp/test.GAMESS.inp", "data/water.xyz"])
    assert_equals(
        open("data/water.inp").read(),
        """ $CONTRL COORD=CART UNITS=ANGS $END

 $DATA
data/water.xyz
C1
O      8.0        0.0584027061        0.0584027059        0.0000000000
H      1.0        1.0096135406       -0.0680162466        0.0000000000
H      1.0       -0.0680162466        1.0096135407        0.0000000000
 $END


""",
    )

    main(["-g", "/tmp/hello.GAMESSUK.inp"])
    main(["/tmp/hello.GAMESSUK.inp", "data/water.xyz"])
    assert_equals(open("data/water.inp").read(), water_mol.to_string("gukin"))

    main(["-g", "/tmp/hello.world.Gaussian.gjf"])
    main(["/tmp/hello.world.Gaussian.gjf", "data/water.xyz"])
    assert_equals(
        open("data/water.gjf").read(),
        """#Put Keywords Here, check Charge and Multiplicity.

 data/water.xyz

0  1
O          0.0584027061        0.0584027059        0.0000000000
H          1.0096135406       -0.0680162466        0.0000000000
H         -0.0680162466        1.0096135407        0.0000000000

""",
    )

    main(["-g", "/tmp/bar.Jaguar.in"])
    main(["/tmp/bar.Jaguar.in", "data/water.xyz"])
    assert_equals(open("data/water.in").read(), water_mol.to_string("jin"))

    main(["-g", "/tmp/foo.Molpro.inp"])
    main(["/tmp/foo.Molpro.inp", "data/water.xyz"])
    assert_equals(open("data/water.inp").read(), water_mol.to_string("mp"))

    main(["-g", "/tmp/example.MOPAC.mop"])
    main(["/tmp/example.MOPAC.mop", "data/water.xyz"])
    assert_equals(
        open("data/water.mop").read(),
        """CHARGE=0 MS=0.0
data/water.xyz

O   0.05840 1  0.05840 1  0.00000 1
H   1.00961 1 -0.06802 1  0.00000 1
H  -0.06802 1  1.00961 1  0.00000 1
""",
    )

    main(["-g", "/tmp/bar.MPQC.in"])
    main(["/tmp/bar.MPQC.in", "data/water.xyz"])
    assert_equals(open("data/water.in").read(), water_mol.to_string("mpqcin"))

    main(["-g", "/tmp/foo.NWChem.nw"])
    main(["/tmp/foo.NWChem.nw", "data/water.xyz"])
    assert_equals(
        open("data/water.nw").read(),
        """start molecule

title data/water.xyz

geometry units angstroms print xyz autosym
O          0.0584027061        0.0584027059        0.0000000000
H          1.0096135406       -0.0680162466        0.0000000000
H         -0.0680162466        1.0096135407        0.0000000000
end
""",
    )

    main(["-g", "/tmp/example.ORCA.inp"])
    main(["/tmp/example.ORCA.inp", "data/water.xyz"])
    assert_equals(
        open("data/water.inp").read(),
        """# data/water.xyz
! Opt

* xyz 0 1
O          0.0584027061        0.0584027059        0.0000000000
H          1.0096135406       -0.0680162466        0.0000000000
H         -0.0680162466        1.0096135407        0.0000000000
*
""",
    )

    main(["-g", "/tmp/bar.Psi.dat"])
    main(["/tmp/bar.Psi.dat", "data/water.xyz"])
    assert_equals(
        open("data/water.dat").read(),
        """# data/water.xyz

molecule {
0 1
O          0.0584027061        0.0584027059        0.0000000000
H          1.0096135406       -0.0680162466        0.0000000000
H         -0.0680162466        1.0096135407        0.0000000000
units angstrom
}

optimize('scf')
""",
    )

    main(["-g", "/tmp/example.QChem.in"])
    main(["/tmp/example.QChem.in", "data/water.xyz"])
    assert_equals(open("data/water.in").read(), water_mol.to_string("qcin"))

    main(["-g", "/tmp/foo.ZINDO.input"])
    main(["/tmp/foo.ZINDO.input", "data/water.xyz"])
    assert_equals(open("data/water.input").read(), water_mol.to_string("zin"))


def _test_example_eda_adf():
    """Test example for EDA in ADF."""
    main(["pnictogen/repo/split.ADF.in", "data/water-dimer.xyz"])
    assert_equals(
        open("data/water-dimer_eda.in").read(),
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

""",
    )
    assert_equals(
        open("data/water-dimer_f1.in").read(),
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

""",
    )
    assert_equals(
        open("data/water-dimer_f2.in").read(),
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

""",
    )


def _test_example_fragments_orca():
    """Test if fragmentation works with ORCA inputs."""
    main(["pnictogen/repo/split.ORCA.inp", "data/water-dimer.xyz"])
    assert_equals(
        open("data/water-dimer.inp").read(),
        """# data/water-dimer.xyz
! Opt

* xyz 0 1
O(1)       0.12908       -0.26336        0.64798
H(1)       0.89795        0.28805        0.85518
H(1)       0.10833       -0.20468       -0.33302
O(2)       0.31020        0.07569       -2.07524
H(2)      -0.26065        0.64232       -2.62218
H(2)       0.64083       -0.57862       -2.71449
*""",
    )


def test_read_with_cclib():
    """Test if we can correctly read with cclib."""
    main(["-g", "/tmp/fnord.Gaussian.gjf"])
    main(["/tmp/fnord.Gaussian.gjf", "data/benzene.out"])
    assert_equals(
        open("data/benzene.gjf").read(),
        """#Put Keywords Here, check Charge and Multiplicity.

 data/benzene.out

0  1
C          1.7458930000        1.7957530000       -1.0597530000
C          0.9484120000        2.8689700000       -1.4311180000
C          1.4480470000        1.0743490000        0.0876540000
C         -0.1470660000        3.2206120000       -0.6552520000
C          0.3525690000        1.4259910000        0.8635200000
C         -0.4449120000        2.4992080000        0.4921550000
H          2.5997410000        1.5203090000       -1.6651660000
H          1.1810280000        3.4311430000       -2.3262420000
H          2.0700040000        0.2375420000        0.3781170000
H         -0.7690240000        4.0574200000       -0.9457150000
H          0.1199530000        0.8638180000        1.7586440000
H         -1.2987600000        2.7746520000        1.0975680000

""",
    )
