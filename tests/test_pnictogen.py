#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glob import iglob
from cinfony import pybel
from nose.tools import assert_equals

from pnictogen import argparser, available_helpers, main, render_template

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
    context = {
        "molecules": list(pybel.readfile("xyz", "examples/water.xyz"))
    }
    context.update(available_helpers)

    main(["-g", "examples/boilerplates/ADF.in"])
    assert_equals(render_template("examples/boilerplates/ADF.in", **context),
                  context["molecules"][0].write("adf"))

    main(["-g", "examples/boilerplates/GAMESS.inp"])
    assert_equals(render_template("examples/boilerplates/GAMESS.inp",
                                  **context),
                  context["molecules"][0].write("gamin"))

    main(["-g", "examples/boilerplates/GAMESSUK.inp"])
    assert_equals(render_template("examples/boilerplates/GAMESSUK.inp",
                                  **context),
                  context["molecules"][0].write("gukin"))

    main(["-g", "examples/boilerplates/Gaussian.gjf"])
    assert_equals(render_template("examples/boilerplates/Gaussian.gjf",
                                  **context),
                  """#Put Keywords Here, check Charge and Multiplicity.

 PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2

0  1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000

""")

    main(["-g", "examples/boilerplates/Jaguar.in"])
    assert_equals(render_template("examples/boilerplates/Jaguar.in",
                                  **context),
                  context["molecules"][0].write("jin"))

    main(["-g", "examples/boilerplates/Molpro.inp"])
    assert_equals(render_template("examples/boilerplates/Molpro.inp",
                                  **context),
                  context["molecules"][0].write("mp"))

    main(["-g", "examples/boilerplates/MOPAC.mop"])
    assert_equals(render_template("examples/boilerplates/MOPAC.mop",
                                  **context),
                  """CHARGE=0 MS=0.0
PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2

O   0.05840 1  0.05840 1  0.00000 1
H   1.00961 1 -0.06802 1  0.00000 1
H  -0.06802 1  1.00961 1  0.00000 1
""")

    main(["-g", "examples/boilerplates/MPQC.in"])
    assert_equals(render_template("examples/boilerplates/MPQC.in", **context),
                  context["molecules"][0].write("mpqcin"))

    main(["-g", "examples/boilerplates/NWChem.nw"])
    assert_equals(render_template("examples/boilerplates/NWChem.nw",
                                  **context),
                  context["molecules"][0].write("nw"))

    main(["-g", "examples/boilerplates/ORCA.inp"])
    assert_equals(render_template("examples/boilerplates/ORCA.inp", **context),
                  """# PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2
! Opt

* xyz 0 1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000
*
""")

    main(["-g", "examples/boilerplates/Psi.dat"])
    assert_equals(render_template("examples/boilerplates/Psi.dat", **context),
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
    assert_equals(render_template("examples/boilerplates/QChem.in", **context),
                  context["molecules"][0].write("qcin"))

    main(["-g", "examples/boilerplates/ZINDO.input"])
    assert_equals(render_template("examples/boilerplates/ZINDO.input",
                                  **context),
                  context["molecules"][0].write("zin"))


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
