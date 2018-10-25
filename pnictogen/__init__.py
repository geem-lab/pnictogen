#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Core functionality."""

import os
import sys
import numpy as np
import argparse
from pkg_resources import require, resource_filename, resource_listdir
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pyrrole import atoms

__version__ = require(__name__)[0].version

# This dict is set to globals prior to template renderization
AVAILABLE_HELPERS = {
    "np": np,
}

REPOSITORY = \
    {os.path.splitext(name)[0]: resource_filename(__name__, "repo/" + name)
     for name in resource_listdir(__name__, "repo")}


def argparser():
    """
    Return a parser for the command-line interface (pnictogen.main).

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
        "template", metavar="template.package.ext | template.ext",
        help="""template file.
        "ext" can be anything.
        "package" might be one of the following:
        {}.""".format(", ".join(REPOSITORY.keys())))
    parser.add_argument(
        "descriptors", metavar="descriptor.ext", nargs="*",
        help="""files describing molecules, which are read using Open Babel
        (run "$ obabel -L formats" for a list of all available file
        formats).""")

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
    Although this function is not intended to be called from Python code (see
    the pnictogen function below for one that is), the following should work:

    >>> import pnictogen
    >>> pnictogen.main(["-g", "/tmp/opt.ORCA.inp"])
    /tmp/opt.ORCA.inp written
    >>> pnictogen.main(["/tmp/opt.ORCA.inp", "data/co.xyz",
    ...                 "data/water.xyz"])
    data/co.inp written
    data/water.inp written

    This is exactly as if pnictogen were called from the command-line.

    """
    parser = argparser()
    args = parser.parse_args(argv)
    package, extension = os.path.basename(args.template).split(".")[-2:]

    if args.generate:
        with open(REPOSITORY[package], "r") as stream:
            content = stream.read()
        with open(args.template, "w") as stream:
            stream.write(content)
        print("{:s} written".format(args.template))
    else:
        for descriptor in args.descriptors:
            input_prefix, _ = os.path.splitext(descriptor)

            try:
                molecule = atoms.read_cclib(descriptor)
                written_files = pnictogen(molecule, input_prefix,
                                          args.template, extension)
            except KeyError:
                molecule = atoms.read_pybel(descriptor)
                written_files = pnictogen(molecule, input_prefix,
                                          args.template, extension)

            for written_file in written_files:
                print("{:s} written".format(written_file))


def pnictogen(molecule, input_prefix, template, extension=None,
              globals=AVAILABLE_HELPERS, **kwargs):
    """
    Generate inputs based on a template and a collection of atoms.

    Parameters
    ----------
    molecule : `pyrrole.Atoms`
        An object with molecular properties.
    input_prefix : str
        Base path (without extension or dot at the end) for the input to be
        generated. All written files will share this common prefix.
    template : str
        Path to Jinja2 template file, relative to the local directory
    extension : str, optional
        File extension common to all generated input files. If not set, the
        template path will be used to select one.
    extensions : list, optional
        A set of extensions that are directly passed to Jinja2
    globals : dict of functions, optional
        Jinja2 specification of functions available within the template (see
        render_template).

    Extra named arguments are passed directly to the template

    Returns
    -------
    written_files : list of str
        A list of paths to generated input files

    Examples
    --------
    This is the function you would call from within Python code. A simple
    example of use would be:

    >>> mol = atoms.read_pybel("data/co.xyz")
    >>> pnictogen(mol, "data/co", "pnictogen/repo/ORCA.inp")
    ['data/co.inp']

    """
    if extension is None:
        package, extension = os.path.basename(template).split(".")[-2:]

    written_files = []

    # TODO: add some keywords from command-line to context.
    raw_rendered = render_template(template, input_prefix=input_prefix,
                                   molecule=molecule, globals=globals,
                                   **kwargs)

    at_id = None
    raw_rendered = raw_rendered.split('--@')
    for rendered in raw_rendered:
        if at_id is None:
            at_id = ""
        else:
            at_id, rendered = rendered.split("\n", 1)
            at_id = "_{:s}".format(at_id)

        if rendered.strip():
            path = "{:s}{:s}.{:s}".format(input_prefix, at_id, extension)
            with open(path, "w") as stream:
                stream.write(rendered)

            written_files.append(path)
    return written_files


def render_template(template, **kwargs):
    """
    Define template rendering with Jinja2.

    Parameters
    ----------
    template : str
        Path to Jinja2 template file, relative to the local directory
    extensions : list, optional
        A set of extensions that are directly passed to Jinja2
    globals : dict of functions, optional
        Jinja2 specification of functions available within the template

    Extra named arguments are passed directly to the template

    Returns
    -------
    str
        The rendered result as returned by Jinja2

    Examples
    --------
    >>> main(["-g", "/tmp/freq.QChem.in"])
    /tmp/freq.QChem.in written
    >>> context = {
    ...     "molecule": atoms.read_pybel("data/water.xyz")
    ... }
    >>> print(render_template("/tmp/freq.QChem.in", **context))
    $comment
    data/water.xyz
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

    """
    extensions = kwargs.pop('extensions', [])
    globals = kwargs.pop('globals', {})

    # TODO: allow and test for templates inheritance (maybe adding something
    # like "~/.pnictogen/" to searchpath as well)
    jinja_env = Environment(
        loader=FileSystemLoader("./"),
        extensions=extensions,
        trim_blocks=True,
    )
    jinja_env.globals.update(globals)

    try:
        template_jinja = jinja_env.get_template(template)
    except TemplateNotFound:
        template_jinja = jinja_env.from_string(open(template).read())

    return template_jinja.render(kwargs)


if __name__ == "__main__":
    main()
