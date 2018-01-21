#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cinfony import pybel
from nose.tools import assert_equals

from pnictogen import available_helpers, render_template

context = {
    "molecules": list(pybel.readfile("xyz", "examples/water.xyz"))
}
context.update(available_helpers)

# TODO: make prettier error messages when runnig tests


def test_render_boilerplates():
    assert_equals(render_template("examples/templates/ADF.in", **context),
                  context["molecules"][0].write("adf"))

    assert_equals(render_template("examples/templates/GAMESS.inp", **context),
                  context["molecules"][0].write("gamin"))

    assert_equals(render_template("examples/templates/GAMESSUK.inp",
                                  **context),
                  context["molecules"][0].write("gukin"))

    assert_equals(render_template("examples/templates/Gaussian.gjf",
                                  **context),
                  """#Put Keywords Here, check Charge and Multiplicity.

 PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2

0  1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000

""")

    assert_equals(render_template("examples/templates/Jaguar.in", **context),
                  context["molecules"][0].write("jin"))

    assert_equals(render_template("examples/templates/Molpro.inp", **context),
                  context["molecules"][0].write("mp"))

    assert_equals(render_template("examples/templates/MOPAC.mop", **context),
                  """CHARGE=0 MS=0.0
PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2

O   0.05840 1  0.05840 1  0.00000 1
H   1.00961 1 -0.06802 1  0.00000 1
H  -0.06802 1  1.00961 1  0.00000 1
""")

    assert_equals(render_template("examples/templates/MPQC.in", **context),
                  context["molecules"][0].write("mpqcin"))

    assert_equals(render_template("examples/templates/NWChem.nw", **context),
                  context["molecules"][0].write("nw"))

    assert_equals(render_template("examples/templates/ORCA.inp", **context),
                  """# PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2
! Opt

* xyz 0 1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000
*
""")

    assert_equals(render_template("examples/templates/Psi.dat", **context),
                  """# PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2

molecule {
0 1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000
units angstrom
}

optimize('scf')""")

    assert_equals(render_template("examples/templates/QChem.in", **context),
                  context["molecules"][0].write("qcin"))

    assert_equals(render_template("examples/templates/ZINDO.input", **context),
                  context["molecules"][0].write("zin"))
