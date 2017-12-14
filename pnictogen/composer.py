#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from mendeleev import element
from jinja2 import Environment, FileSystemLoader

TEMPLATES_PATH = [
    './',
    '~/.pnictogen/',
    os.path.join(os.path.dirname(__file__), '../templates/')
]

_jinja2loader = FileSystemLoader(TEMPLATES_PATH, followlinks=True)
_jinja2env = Environment(loader=_jinja2loader, lstrip_blocks=True,
                         trim_blocks=True, keep_trailing_newline=True)
_jinja2env.globals.update(element=element)


def render_template(template, context={}):
    """
    Shortcut for rendering Jinja2 templates

    Parameters
    ----------
    template : str
        Content of a Jinja2 template. It will be rendered in an environment
        where inheritance is available.
    context : dict, optional

    Examples
    --------
    A template can be rendered with the following:

    >>> print(render_template(template="Hello {{ something }}!",
    ...                       context={"something": "world"}))
    Hello world!
    """

    return _jinja2env.from_string(template).render(context)


class Composer(object):
    """
    An input composition system

    Parameters
    ----------
    template : file or str
        File, path to file or content for a Jinja2 template
    molecules : list of Molecule
        A list of Molecule instances
    cli : dict, optional
        A representation of the call if called from the command-line:
        cli["parser"] should be a argparse.ArgumentParser object,
        cli["args"] should store its parsed arguments and cli["molecule"]
        should correspond to the path of the molecule file.

    Examples
    --------
    A minimal example would be:

    >>> from pnictogen.molecule import Molecule
    >>> c = Composer("Hello {{ molecules[0].title }}!", [Molecule("O=C=O")])
    >>> print(c)
    Hello O=C=O!

    You can still get data from molecules after you created an input:

    >>> t = "examples/templates/ORCA.inp"
    >>> m = Molecule("1\\nHydride\\nH\\t0.0 0.0 0.0", "xyz")
    >>> c = Composer(t, [m])
    >>> m.charge, m.spin = -1, 1
    >>> c.molecules[0].charge, c.molecules[0].spin, c.molecules[0].title
    (-1, 1, 'Hydride')

    Lots of things are available for your template:

    >>> c = Composer(\"\"\"title = {{ molecules[0].title }}
    ...
    ... charge, spin = {{ molecules[0].charge }}, {{ molecules[0].spin }}
    ... {{ molecules[0].write("simplexyz") -}}\"\"\", [m])
    >>> print(c)
    title = Hydride
    <BLANKLINE>
    charge, spin = -1, 1
    H          0.00000        0.00000        0.00000

    You can use all features Jinja2 offers, such as template inheritance:

    >>> with open("examples/water.xyz") as stream:
    ...     m = Molecule(stream.read(), "xyz")
    >>> c = Composer('{% extends "examples/templates/ORCA.inp" %}', [m])
    >>> print(c)
    # PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2
    ! Opt
    <BLANKLINE>
    * xyz 0 1
    O          0.05840        0.05840        0.00000
    H          1.00961       -0.06802        0.00000
    H         -0.06802        1.00961        0.00000
    *
    <BLANKLINE>
    """

    def __init__(self, template, molecules, cli=None, *args, **kwargs):
        try:
            with open(template) as stream:
                self.template = stream.read()
        except IOError:
            try:
                self.template = template.read()
            except AttributeError:
                # FIX: we end up here if file does not exist!
                self.template = template

        self.molecules = molecules

        self.cli = cli
        self.package = type(self)

        self.__dict__.update(kwargs)

    def __str__(self):
        return render_template(self.template, self.__dict__)
