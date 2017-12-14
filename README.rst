Welcome to pnictogen
====================

pnictogen_ is both a library and a command-line tool that helps composing input
files for computational chemistry packages.
It is based on Jinja2_, a modern and friendly templating language for Python:

.. code:: bash

   $ # generate a minimal template for you to edit
   $ pnictogen -g new_template.ORCA.inp
   $ # using new_template.inp creates a blank file
   $ cat new_template.ORCA.inp
   # {{ molecules[0].title }}
   ! Opt

   * xyz {{ molecules[0].charge }} {{ molecules[0].spin }}
   {{ molecules[0].write("simplexyz") }}
   *
   $ # make your edits
   $ # create your inputs for ORCA
   $ pnictogen new_template.ORCA.inp molecule_one.xyz molecule_two.pdb

pnictogen is the big brother of nitrogen_, hence the
`name <https://en.wikipedia.org/wiki/Pnictogen>`_.

.. _pnictogen: https://github.com/dudektria/pnictogen
.. _nitrogen: https://github.com/chemical-scripts/nitrogen
.. _Jinja2: http://jinja.pocoo.org/docs/latest/
