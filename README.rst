Welcome to pnictogen
====================

pnictogen_ is both a library and a command-line tool that helps composing input
files for computational chemistry packages.
It is based on Jinja2_, a modern and friendly templating language for Python:

.. code:: bash

   $ # generate a minimal template for you to edit
   $ pnictogen -g new_template.ORCA.inp
   new_template.ORCA.inp written
   $ # using new_template.inp creates a blank file
   $ cat new_template.ORCA.inp
   # {{ molecules[0].title }}
   ! Opt

   * xyz {{ molecules[0].charge }} {{ molecules[0].spin }}
   {{ coords(molecules[0], "xyz") }}
   *
   $ # make your edits
   $ # create your inputs for ORCA
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
