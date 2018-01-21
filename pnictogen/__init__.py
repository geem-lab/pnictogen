#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import argparse
import pkg_resources
from jinja2 import Environment, FileSystemLoader
from cinfony import pybel

from pnictogen.helpers import available_helpers

__version__ = pkg_resources.require(__name__)[0].version

with open(os.path.join(os.path.dirname(__file__), "../config.yml")) as stream:
    config = yaml.load(stream)


def argparser():
    """
    Return a parser for the command-line interface (pnictogen.main)

    Returns
    -------
    argparse.ArgumentParser

    Examples
    --------
    For reproducing the behaviour of pnictogen in the command-line, the
    following can be used:

    >>> from pnictogen import argparser
    >>> parser = argparser()
    >>> argv = ["template.ORCA.inp",  # a real application would use
    ...         "1.xyz", "2.pdb"]     # sys.argv[1:] instead
    >>> args = parser.parse_args(argv)

    parser is then an argparse.ArgumentParser object and args an object
    representing parsed arguments.
    """

    parser = argparse.ArgumentParser(
        description="input generation for computational chemistry packages",
        epilog="""%(prog)s is licensed under the MIT License
        <https://github.com/dudektria/%(prog)s>""")

    parser.add_argument(
        "-g", "--generate", action="store_true",
        help="create a simple boilerplate input template for you to modify")
    parser.add_argument(
        "-v", "--version",
        action="version", version="%(prog)s {:s}".format(__version__))

    # TODO: manpage
    parser.add_argument(
        "template_name", metavar="template.package.ext | template.ext",
        help="""template file.
        "ext" can be anything.
        "package" might be one of the following:
        {}.""".format(", ".join(config["packages"].keys())))
    parser.add_argument(
        "descriptors", metavar="descriptor.ext", nargs="*",
        help="""files describing molecules, which are read using Open Babel
        (execute "$ obabel -L formats" for a full list of possible file
        types).""")

    return parser


def main(argv=sys.argv[1:]):
    """
    Pnictogen command-line interface. It writes inputs for sets of molecules.

    Parameters
    ----------
    argv : list of str
        Arguments as taken from the command-line

    Examples
    --------
    Although this function is not intended to be called from Python code, the
    following should work:

    >>> import pnictogen
    >>> pnictogen.main(["-g", "examples/templates/ORCA.inp"])
    examples/templates/ORCA.inp written
    >>> pnictogen.main(["examples/templates/ORCA.inp", "examples/co.xyz",
    ...                 "examples/water.xyz"])
    examples/co.inp written
    examples/water.inp written

    This is exactly as if pnictogen were called from the command-line.
    """

    parser = argparser()
    args = parser.parse_args(argv)
    package, template_extension = \
        os.path.basename(args.template_name).split(".")[-2:]

    if args.generate:
        with open(args.template_name, "w") as stream:
            if package in config["packages"]:
                stream.write(config["packages"][package]["boilerplate"])
        print("{:s} written".format(args.template_name))
    else:
        for descriptor in args.descriptors:
            name, descriptor_extension = os.path.splitext(descriptor)
            path = "{:s}.{:s}".format(name, template_extension)

            # TODO: try cclib before Open Babel
            # TODO: try to use data in titles (e.g. charge/spin)
            molecules = list(pybel.readfile(descriptor_extension[1:],
                                            descriptor))
            # TODO: add some keywords from command-line to context (like
            # "-k charge=-1" or from a yaml file)
            rendered = render_template(args.template_name, molecules=molecules,
                                       globals=available_helpers)

            with open(path, "w") as stream:
                stream.write(rendered)
            print("{:s} written".format(path))


def render_template(template_name, **context):
    """
    Define template rendering with Jinja2

    Parameters
    ----------
    template_name : str
        Path to template, relative to the local directory
    extensions : list
        Extensions to Jinja2
    globals : dict
        Jinja2 specification of objects available within templates

    Extra parameters are passed directly to the template

    Returns
    -------
    str
        The rendered result as returned by Jinja2

    Examples
    --------
    >>> context = {
    ...     "molecules": list(pybel.readfile("xyz", "examples/water.xyz"))
    ... }
    >>> print(render_template("examples/templates/QChem.in", **context))
    $comment
    PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2
    $end
    <BLANKLINE>
    $molecule
    0 1
    8 0.0584027 0.0584027 0
    1 1.00961 -0.0680162 0
    1 -0.0680162 1.00961 0
    $end
    <BLANKLINE>
    $rem
    <BLANKLINE>
    $end
    <BLANKLINE>
    """
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    # TODO: allow and test for templates inheritance (maybe adding something
    # like "~/.pnictogen/" to searchpath as well)
    jinja_env = Environment(
        loader=FileSystemLoader("./"),
        extensions=extensions,
    )
    jinja_env.globals.update(globals)

    return jinja_env.get_template(template_name).render(context)


if __name__ == "__main__":
    main()
