#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glob import iglob
from cinfony import pybel
from nose.tools import assert_equals

from pnictogen import argparser, main

# Only testing xyz files because I trust Open Babel to handle other file types
example_xyz_files = iglob("examples/*.xyz")
boilerplates = iglob("examples/boilerplates/*")

# TODO: make prettier error messages when runnig tests


def test_argparser():
    for template in boilerplates:
        argv = [template] + list(example_xyz_files)

        parser = argparser()
        parser.parse_args(argv)


def test_main():
    for template in boilerplates:
        main(["-g", template])

        # One at a time
        for xyz_file in example_xyz_files:
            main([template, xyz_file])

        # All at once
        main([template] + list(example_xyz_files))


def test_conformers():
    main(["examples/templates/all.MOPAC.mop",
          "examples/pentane_conformers.xyz"])


# TODO: create hello world template in a temporary file to test
# render_template() without any molecule.
# def test_render_templates():
#     pass


def test_render_boilerplates():
    water_mol = pybel.readfile("xyz", "examples/water.xyz").next()

    main(["-g", "examples/boilerplates/ADF.in"])
    main(["examples/boilerplates/ADF.in", "examples/water.xyz"])
    assert_equals(open("examples/water.in").read(), water_mol.write("adf"))

    main(["-g", "examples/boilerplates/GAMESS.inp"])
    main(["examples/boilerplates/GAMESS.inp", "examples/water.xyz"])
    assert_equals(open("examples/water.inp").read(), water_mol.write("gamin"))

    main(["-g", "examples/boilerplates/GAMESSUK.inp"])
    main(["examples/boilerplates/GAMESSUK.inp", "examples/water.xyz"])
    assert_equals(open("examples/water.inp").read(), water_mol.write("gukin"))

    main(["-g", "examples/boilerplates/Gaussian.gjf"])
    main(["examples/boilerplates/Gaussian.gjf", "examples/water.xyz"])
    assert_equals(open("examples/water.gjf").read(),
                  """#Put Keywords Here, check Charge and Multiplicity.

 PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2

0  1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000

""")

    main(["-g", "examples/boilerplates/Jaguar.in"])
    main(["examples/boilerplates/Jaguar.in", "examples/water.xyz"])
    assert_equals(open("examples/water.in").read(), water_mol.write("jin"))

    main(["-g", "examples/boilerplates/Molpro.inp"])
    main(["examples/boilerplates/Molpro.inp", "examples/water.xyz"])
    assert_equals(open("examples/water.inp").read(), water_mol.write("mp"))

    main(["-g", "examples/boilerplates/MOPAC.mop"])
    main(["examples/boilerplates/MOPAC.mop", "examples/water.xyz"])
    assert_equals(open("examples/water.mop").read(),
                  """CHARGE=0 MS=0.0
PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2

O   0.05840 1  0.05840 1  0.00000 1
H   1.00961 1 -0.06802 1  0.00000 1
H  -0.06802 1  1.00961 1  0.00000 1
""")

    main(["-g", "examples/boilerplates/MPQC.in"])
    main(["examples/boilerplates/MPQC.in", "examples/water.xyz"])
    assert_equals(open("examples/water.in").read(), water_mol.write("mpqcin"))

    main(["-g", "examples/boilerplates/NWChem.nw"])
    main(["examples/boilerplates/NWChem.nw", "examples/water.xyz"])
    assert_equals(open("examples/water.nw").read(), water_mol.write("nw"))

    main(["-g", "examples/boilerplates/ORCA.inp"])
    main(["examples/boilerplates/ORCA.inp", "examples/water.xyz"])
    assert_equals(open("examples/water.inp").read(),
                  """# PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2
! Opt

* xyz 0 1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000
*
""")

    main(["-g", "examples/boilerplates/Psi.dat"])
    main(["examples/boilerplates/Psi.dat", "examples/water.xyz"])
    assert_equals(open("examples/water.dat").read(),
                  """# PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2

molecule {
0 1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000
units angstrom
}

optimize('scf')""")

    main(["-g", "examples/boilerplates/QChem.in"])
    main(["examples/boilerplates/QChem.in", "examples/water.xyz"])
    assert_equals(open("examples/water.in").read(), water_mol.write("qcin"))

    main(["-g", "examples/boilerplates/ZINDO.input"])
    main(["examples/boilerplates/ZINDO.input", "examples/water.xyz"])
    assert_equals(open("examples/water.input").read(), water_mol.write("zin"))


def test_keywords_in_title():
    main(["-g", "examples/boilerplates/Gaussian.gjf"])
    main(["examples/boilerplates/Gaussian.gjf", "examples/hydroxide.xyz"])

    assert_equals(open("examples/hydroxide.gjf").read(),
                  """#Put Keywords Here, check Charge and Multiplicity.

 This guy has charge=-1 but its multiplicity spin=2 is incorrect

-1  2
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000

""")
