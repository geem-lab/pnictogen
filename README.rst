Welcome to pnictogen
====================

pnictogen_ is both a library and a command-line tool that helps composing input
files for computational chemistry packages.
It is based on Jinja2_, a modern and friendly templating language for Python:

.. code:: bash

    $ cat new_template.ORCA.inp
    # {{ molecules[0].title }}
    ! Opt

    * xyz {{ molecules[0].charge }} {{ molecules[0].spin }}
    {{ coords(molecules[0], "xyz") }}
    *
    $ pnictogen new_template.ORCA.inp examples/water.xyz
    examples/water.inp written
    $ cat examples/water.inp
    # A water molecule
    ! Opt

    * xyz 0 1
    O          0.05840        0.05840        0.00000
    H          1.00961       -0.06802        0.00000
    H         -0.06802        1.00961        0.00000
    *

pnictogen is the big brother of nitrogen_, hence the
`name <https://en.wikipedia.org/wiki/Pnictogen>`_.

.. _pnictogen: https://github.com/dudektria/pnictogen
.. _nitrogen: https://github.com/chemical-scripts/nitrogen
.. _Jinja2: http://jinja.pocoo.org/docs/latest/

Tutorial
--------

pnictogen can currently create boilerplates for
`ADF <https://www.scm.com/product/adf/>`_,
`GAMESS (US) <http://www.msg.ameslab.gov/GAMESS/GAMESS.html>`_,
`GAMESS-UK <http://www.cfs.dl.ac.uk/>`_,
`Gaussian <http://www.gaussian.com/>`_,
`Jaguar <http://www.schrodinger.com/ProductDescription.php?mID=6&sID=9>`_,
`Molpro <http://www.molpro.net/>`_,
`MOPAC <http://openmopac.net/>`_,
`MPQC <http://www.mpqc.org/>`_,
`NWChem <http://www.nwchem-sw.org/index.php/Main_Page>`_,
`ORCA <http://www.thch.uni-bonn.de/tc/orca/>`_,
`Psi <http://psicode.org/>`_,
`Q-Chem <http://q-chem.com/>`_
and
`ZINDO <https://comp.chem.umn.edu/zindo-mn/>`_:

.. code:: bash

    $ pnictogen -g new_template.MOPAC.mop
    new_template.MOPAC.mop written
    $ cat new_template.MOPAC.mop
    CHARGE={{ molecules[0].charge }} MS={{ (molecules[0].spin - 1)/2 }}
    {{ molecules[0].title }}

    {{ coords(molecules[0], "mop") }}

(``pnictogen -g new_template.inp`` creates a blank file.)

You can either create and edit a boilerplate template or start fresh.
Once you have a template, generating inputs is easy:

.. code:: bash

    $ pnictogen new_template.ORCA.inp examples/co.xyz examples/water.xyz
    examples/co.inp written
    examples/water.inp written

(Wildcards are allowed, e.g., ``pnictogen new_template.ORCA.inp *.xyz`` works.)

Since
pnictogen is built on top of `Cinfony <http://cinfony.github.io/>`_, it is able to read anything `Open Babel <http://openbabel.org/wiki/Main_Page>`_ reads.
Check the list of all available file formats `here <http://openbabel.org/docs/2.3.0/FileFormats/Overview.html>`_.

Templates
---------

You can use the full Jinja2 syntax within templates (check `here <http://jinja.pocoo.org/docs/2.10/templates/>`_ its documentation for details).

Besides this, pnictogen also understands a special delimiter (``--@``) that allows one to generate many inputs from a single file:

.. code:: bash

    $ cat examples/templates/all.MOPAC.mop
    {% for molecule in molecules %}
    --@{{ loop.index }}
    CHARGE={{ molecule.charge }} MS={{ (molecule.spin - 1)/2 }}
    {{ molecule.title }}

    {{ coords(molecule, "mop") }}

    {% endfor %}
    $ pnictogen examples/templates/all.MOPAC.mop examples/pentane_conformers.xyz
    examples/pentane_conformers_1.mop written
    examples/pentane_conformers_2.mop written
    examples/pentane_conformers_3.mop written
    examples/pentane_conformers_4.mop written
    examples/pentane_conformers_5.mop written
    examples/pentane_conformers_6.mop written
    examples/pentane_conformers_7.mop written
    examples/pentane_conformers_8.mop written
    examples/pentane_conformers_9.mop written

The rest of the line after ``--@`` is aways added to the name of the inputs after an underscore (``_``).

In the example above, ``examples/pentane_conformers.xyz`` contains nine conformers of pentane, so nine inputs were generated (the counting is provided by ``loop.index``):

.. code:: bash

    $ cat examples/pentane_conformers_5.mop
    CHARGE=0 MS=0.0
    C5H12

    C   2.49842 1 -0.31168 1 -0.01981 1
    C   1.24920 1  0.57161 1  0.00000 1
    C  -0.00000 1 -0.31179 1 -0.00000 1
    C  -1.24920 1  0.57161 1 -0.00000 1
    C  -1.25904 1  1.44091 1 -1.25912 1
    H   2.50545 1 -0.95092 1  0.86305 1
    H   2.49134 1 -0.93096 1 -0.91678 1
    H   3.38842 1  0.31762 1 -0.01981 1
    H   1.25629 1  1.19089 1  0.89697 1
    H   1.24217 1  1.21085 1 -0.88286 1
    H  -0.00000 1 -0.94109 1 -0.89000 1
    H  -0.00000 1 -0.94109 1  0.89000 1
    H  -2.13917 1 -0.05758 1  0.01408 1
    H  -1.24214 1  1.21089 1  0.88283 1
    H  -0.36907 1  2.07009 1 -1.27320 1
    H  -1.26610 1  0.80162 1 -2.14194 1
    H  -2.14898 1  2.07029 1 -1.25918 1
