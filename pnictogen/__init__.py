#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import argparse
import pkg_resources

from .composer import Composer
from pnictogen.molecule import read_molecules, supported_extensions_dict

__version__ = pkg_resources.require(__name__)[0].version

with open(os.path.join(os.path.dirname(__file__), "../config.yml")) as stream:
    config = yaml.load(stream)

supported_packages = config["packages"].keys()
supported_packages_desc = " or ".join([", ".join(supported_packages[:-1]),
                                      supported_packages[-1]])

supported_extensions = ["{} ({})".format(k, v) for k, v
                        in supported_extensions_dict.items()]
supported_extensions_desc = " or ".join([", ".join(supported_extensions[:-1]),
                                        supported_extensions[-1]])


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
    representing parsed arguments. Both objects can be used in your code in
    order to reproduce the bevahiour of pnictogen if so desired.
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

    parser.add_argument(
        "template", metavar="template.package.ext | template.ext",
        help="""template file.
        "ext" can be anything.
        "package" might be one of the following:
        {}.""".format(supported_packages_desc))
    parser.add_argument(
        "descriptors", metavar="descriptor.ext", nargs="*",
        help="""files describing molecules.
        "ext" can be one of the following:
        {}. Please check Open Babel documentation for
        more about these formats.""".format(supported_extensions_desc))

    return parser


def main(argv=sys.argv[1:]):
    """
    Pnictogen command-line interface. It writes inputs for sets of molecules.

    Examples
    --------
    Although this function is not intended to be called from Python code, the
    following should work:

    >>> import pnictogen
    >>> pnictogen.main(["examples/template/ORCA.inp", "examples/co.xyz",
    ...                 "examples/water.xyz"])
    examples/co.inp written
    examples/water.inp written

    This is exactly as if pnictogen were called from the command-line.
    """

    parser = argparser()
    args = parser.parse_args(argv)

    cli = {"args": args, "parser": parser}

    package, template_extension = \
        os.path.basename(args.template).split(".")[-2:]

    if args.generate:
        with open(args.template, "w") as stream:
            if package in config["packages"]:
                stream.write(config["packages"][package]["boilerplate"])

        print("{:s} written".format(args.template))
    else:
        for descriptor in args.descriptors:
            cli["molecule"] = os.path.abspath(descriptor)

            basename, descriptor_extension = os.path.splitext(descriptor)
            input_path = "{:s}.{:s}".format(basename, template_extension)

            cli["output"] = os.path.abspath(input_path)

            try:
                mols = read_molecules(descriptor, descriptor_extension[1:])
                rendered = str(Composer(args.template, mols, cli))
            except IOError as e:
                raise parser.error(e)

            with open(input_path, "w") as stream:
                stream.write(rendered)

            print("{:s} written".format(input_path))


if __name__ == "__main__":
    main()
