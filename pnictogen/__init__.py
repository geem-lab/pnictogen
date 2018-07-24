#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import parse
import argparse
import pkg_resources
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import pybel

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
        "template", metavar="template.package.ext | template.ext",
        help="""template file.
        "ext" can be anything.
        "package" might be one of the following:
        {}.""".format(", ".join(config["packages"].keys())))
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
    package, extension = os.path.basename(args.template).split(".")[-2:]

    if args.generate:
        with open(args.template, "w") as stream:
            if package in config["packages"]:
                stream.write(config["packages"][package]["boilerplate"])
        print("{:s} written".format(args.template))
    else:
        for descriptor in args.descriptors:
            input_prefix, descriptor_extension = os.path.splitext(descriptor)

            # TODO: try cclib before Open Babel
            molecules = list(pybel.readfile(descriptor_extension[1:],
                                            descriptor))

            for molecule in molecules:
                update_data(molecule, molecule.title)

            written_files = pnictogen(molecules, input_prefix, args.template,
                                      extension)

            for written_file in written_files:
                print("{:s} written".format(written_file))


def pnictogen(molecules, input_prefix, template, extension=None,
              globals=available_helpers, **kwargs):
    """
    Generate inputs based on a template and a set of molecules

    Parameters
    ----------
    molecules : iterable object of pybel.Molecule
        A set of molecules. This will be converted to list before being passed
        to template.
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

    >>> mol = pybel.readfile("xyz", "examples/co.xyz")
    >>> pnictogen(mol, "examples/co", "examples/templates/ORCA.inp")
    ['examples/co.inp']
    """
    if extension is None:
        package, extension = os.path.basename(template).split(".")[-2:]

    written_files = []

    # TODO: add some keywords from command-line to context (like
    # "-k charge=-1" or from a yaml file)
    raw_rendered = render_template(template, input_prefix=input_prefix,
                                   molecules=list(molecules),
                                   globals=globals, **kwargs)

    flag = None
    raw_rendered = raw_rendered.split('--@')
    for rendered in raw_rendered:
        if flag is None:
            flag = ""
        else:
            flag, rendered = rendered.split("\n", 1)
            flag = "_{:s}".format(flag)

        if rendered.strip():
            path = "{:s}{:s}.{:s}".format(input_prefix, flag, extension)
            with open(path, "w") as stream:
                stream.write(rendered)

            written_files.append(path)
    return written_files


def render_template(template, **kwargs):
    """
    Define template rendering with Jinja2

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
    >>> main(["-g", "examples/templates/QChem.in"])
    examples/templates/QChem.in written
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


def update_data(molecule, line,
                pattern=parse.compile("{key:S}={value:S}")):
    """
    Update the data stored in molecule with what can be parsed from a string

    Parameters
    ----------
    molecule : pybel.Molecule
        The molecule to be updated
    line : str
        The string to be parsed
    pattern : parse.Parser, optional
        A parse.Parser instance to parse line

    Examples
    --------
    Currently only charge and spin are parsed:

    >>> mol = pybel.readstring("smi", "[Cu]")
    >>> mol.charge, mol.spin
    (0, 1)
    >>> update_data(mol, "charge=+1 spin=3")
    >>> mol.charge, mol.spin
    (1, 3)
    """
    for result in pattern.findall(line):
        if result["key"] == "charge":
            molecule.OBMol.SetTotalCharge(int(result["value"]))
        elif result["key"] == "spin":
            molecule.OBMol.SetTotalSpinMultiplicity(int(result["value"]))


if __name__ == "__main__":
    main()
