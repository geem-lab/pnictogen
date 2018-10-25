.. |build-badge| image:: https://travis-ci.org/dudektria/pnictogen.svg?branch=master
   :target: https://travis-ci.org/dudektria/pnictogen
   :alt: Travis CI Status

.. |pypi-badge| image:: https://badge.fury.io/py/pnictogen.svg
   :target: https://badge.fury.io/py/pnictogen
   :alt: PyPI Version

|build-badge| |pypi-badge|

Welcome to pnictogen
====================

pnictogen_ is both a library and a command-line tool that helps composing input
files for computational chemistry packages.
It is based on Jinja2_, a modern and friendly templating language for Python:

.. code:: bash

    $ cat new_template.ORCA.inp
    # {{ molecule.name }}
    ! Opt

    * xyz {{ molecule.charge }} {{ molecule.mult }}
    {{ molecule.to_string("xyz") }}
    *
    $ pnictogen new_template.ORCA.inp data/water.xyz
    data/water.inp written
    $ cat data/water.inp
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

Installation
------------

You can get pnictogen directly from PyPI:

.. code:: bash

    $ pip install -U pnictogen

The above will install the the version from PyPI, which is recommended.

For the development version, clone this repository and run:

.. code:: bash

    $ pip install -U -e .

Tutorial
--------

pnictogen can currently create boilerplates for
`ADF <https://www.scm.com/product/adf/>`_,
`DALTON <http://daltonprogram.org/>`_,
`GAMESS (US) <http://www.msg.ameslab.gov/GAMESS/GAMESS.html>`_,
`GAMESS-UK <http://www.cfs.dl.ac.uk/>`_,
`Gaussian <http://www.gaussian.com/>`_,
`Jaguar <https://www.schrodinger.com/jaguar>`_,
`Molpro <http://www.molpro.net/>`_,
`MOPAC <http://openmopac.net/>`_,
`MPQC <http://www.mpqc.org/>`_,
`NWChem <http://www.nwchem-sw.org/index.php/Main_Page>`_,
`ORCA <https://orcaforum.cec.mpg.de/>`_,
`Psi <http://psicode.org/>`_,
`Q-Chem <http://q-chem.com/>`_
and
`ZINDO <https://comp.chem.umn.edu/zindo-mn/>`_:

.. code:: bash

    $ pnictogen -g new_template.MOPAC.mop
    new_template.MOPAC.mop written
    $ cat new_template.MOPAC.mop
    CHARGE={{ molecule.charge }} MS={{ (molecule.mult - 1)/2 }}
    {{ molecule.name }}

    {{ molecule.to_string("mop") }}

(``pnictogen -g new_template.inp`` creates a blank file.)

You can either create and edit a boilerplate template or start fresh.
Once you have a template, generating inputs is easy:

.. code:: bash

    $ pnictogen new_template.ORCA.inp data/co.xyz data/water.xyz
    data/co.inp written
    data/water.inp written

(Wildcards are allowed, e.g., ``pnictogen new_template.ORCA.inp *.xyz`` works.)

Since
pnictogen is built on top of `Pybel <https://open-babel.readthedocs.io/en/latest/UseTheLibrary/Python_PybelAPI.html>`_, so it is able to read anything `Open Babel <http://openbabel.org/wiki/Main_Page>`_ reads.
Check the list of all available file formats `here <https://open-babel.readthedocs.io/en/latest/FileFormats/Overview.html>`_.

Templates
---------

You can use the full Jinja2 syntax within templates (`check here <http://jinja.pocoo.org/docs/2.10/templates/>`_ its documentation for details).

Besides this, pnictogen also understands a special delimiter (``--@``) that allows one to generate many inputs from a single file:

.. code:: bash

    $ cat repo/MOPAC.mop
    {% for molecule in molecule %}
    --@{{ loop.index }}
    CHARGE={{ molecule.charge }} MS={{ (molecule.mult - 1)/2 }}
    {{ molecule.name }}

    {{ molecule.to_string("mop") }}

    {% endfor %}
    $ pnictogen repo/MOPAC.mop data/pentane_conformers.xyz
    data/pentane_conformers_1.mop written
    data/pentane_conformers_2.mop written
    data/pentane_conformers_3.mop written
    data/pentane_conformers_4.mop written
    data/pentane_conformers_5.mop written
    data/pentane_conformers_6.mop written
    data/pentane_conformers_7.mop written

The rest of the line after ``--@`` is aways added to the name of the inputs after an underscore (``_``).

In the example above, ``data/pentane_conformers.xyz`` contains seven conformers of pentane, so seven inputs were generated (the counting is provided by ``loop.index``):

.. code:: bash

    $ cat data/pentane_conformers_5.mop
    CHARGE=0 MS=0.0
    C5H12

    C   1.23923 1  1.46892 1 -1.23930 1
    C   1.24920 1  0.57161 1  0.00000 1
    C  -0.00000 1 -0.31179 1 -0.00000 1
    C  -1.24920 1  0.57161 1 -0.00000 1
    C  -2.49842 1 -0.31168 1  0.01981 1
    H   1.23217 1  0.84960 1 -2.13625 1
    H   0.34926 1  2.09811 1 -1.22516 1
    H   2.12917 1  2.09831 1 -1.23936 1
    H   2.13917 1 -0.05758 1 -0.01415 1
    H   1.25625 1  1.19094 1  0.89694 1
    H  -0.00000 1 -0.94109 1 -0.89000 1
    H  -0.00000 1 -0.94109 1  0.89000 1
    H  -1.24217 1  1.21085 1  0.88286 1
    H  -1.25629 1  1.19089 1 -0.89697 1
    H  -2.50545 1 -0.95092 1 -0.86305 1
    H  -2.49134 1 -0.93096 1  0.91678 1
    H  -3.38842 1  0.31762 1  0.01981 1

Example: energy decomposition analysis (EDA) with ADF
--------------------------------------------------------------

Imagine we want to do `energy decomposition analysis <https://doi.org/10.1002/wcms.71>`_ on the following water dimer:

.. code:: bash

        $ cat water-dimer.xyz
        6

        O          0.12908       -0.26336        0.64798
        H          0.89795        0.28805        0.85518
        H          0.10833       -0.20468       -0.33302
        O          0.31020        0.07569       -2.07524
        H          0.64083       -0.57862       -2.71449
        H         -0.26065        0.64232       -2.62218

The following template uses both ``Atoms.split()`` and ``Atoms.to_string("xyz")`` functions to generate ADF inputs in bulk:

.. code:: bash

    $ cat split.ADF.in
    {% set frags = molecule.split([range(3), range(3, 6)]) %}
    --@eda
    ATOMS Cartesian
    {% for frag in frags %}
    {{ frag.to_string("xyz", dialect="adf", fragment_id="f{}".format(loop.index)) }}
    {% endfor %}
    End

    Fragments
    {% for frag in frags %}
     f{{ loop.index }} {{ input_prefix }}_f{{ loop.index }}.t21
    {% endfor %}
    End

    {% for frag in frags %}
    --@f{{ loop.index }}
    ATOMS Cartesian
    {{ frag.to_string("xyz") }}
    End

    {% endfor %}
    $ pnictogen split.ADF.in data/water-dimer.xyz
    data/water-dimer_eda.in written
    data/water-dimer_f1.in written
    data/water-dimer_f2.in written

The above creates inputs like the following:

.. code:: bash

    $ cat water-dimer_eda.in
    ATOMS Cartesian
    O          0.12908       -0.26336        0.64798       f=f1
    H          0.89795        0.28805        0.85518       f=f1
    H          0.10833       -0.20468       -0.33302       f=f1
    O          0.31020        0.07569       -2.07524       f=f2
    H          0.64083       -0.57862       -2.71449       f=f2
    H         -0.26065        0.64232       -2.62218       f=f2
    End

    Fragments
    f1 data/water-dimer_f1.t21
    f2 data/water-dimer_f2.t21
    End

    $ cat water-dimer_f1.in
    ATOMS Cartesian
    O          0.12908       -0.26336        0.64798
    H          0.89795        0.28805        0.85518
    H          0.10833       -0.20468       -0.33302
    End
