#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Core functionality."""

import os
import sys
import argparse
import importlib
from pkg_resources import require, resource_filename, resource_listdir

import cclib
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

__version__ = require(__name__)[0].version

table = cclib.parser.utils.PeriodicTable()

REPOSITORY = {
    os.path.splitext(name)[0]: resource_filename(__name__, "repo/" + name)
    for name in resource_listdir(__name__, "repo")
}


class Atoms:
    """
    This is a simple umbrella object for many sources of data so as to make
    everything behave like ``cclib.parser.ccData``.

    Parameters
    ----------
    data : ccData-like
        Any object that behaves like ``cclib.parser.ccData``.

    """

    def __init__(self, data):
        """See docstring for this class."""
        self._data = data

        if not hasattr(self._data, "name"):
            self.name = ""

        if self._data.atomcoords.ndim > 2:
            self.atomcoords = self._data.atomcoords
        else:
            self.atomcoords = [self._data.atomcoords]

        self.atomnos = self._data.atomnos

        try:
            self.charge = self._data.charge
        except AttributeError:
            self.charge = 0

        try:
            self.mult = self._data.mult
        except AttributeError:
            self.mult = 1

        if not hasattr(self._data, "atomsymbols"):
            self.atomsymbols = [table.element[atomno] for atomno in self.atomnos]

    def __getattr__(self, value):
        """Wrap `Atoms.value` into `Atoms._data.value`."""
        return getattr(self._data, value)

    def to_openbabel(self):
        """Return a OBMol."""
        obmol = cclib.bridge.makeopenbabel(
            self.atomcoords, self.atomnos, self.charge, self.mult
        )
        obmol.SetTitle(self.name)
        return obmol

    def to_string(self, format="xyz", with_header=False, with_atomnos=False):
        if format == "xyz":
            if with_atomnos:
                s = "\n".join(
                    [
                        f"{s:3s} {n:-6.1f} {c[0]:-19.10f} {c[1]:-19.10f} {c[2]:-19.10f}"
                        for s, n, c in zip(
                            self.atomsymbols, self.atomnos, self.atomcoords[-1]
                        )
                    ]
                )
            else:
                s = "\n".join(
                    [
                        f"{s:3s} {c[0]:-19.10f} {c[1]:-19.10f} {c[2]:-19.10f}"
                        for s, c in zip(self.atomsymbols, self.atomcoords[-1])
                    ]
                )

            if with_header:
                s = f"{len(self.atomnos)}\n{self.name}\n{s}"
            return s
        else:
            obc = cclib.bridge.cclib2openbabel.ob.OBConversion()
            if obc.SetOutFormat(format):
                return obc.WriteString(self.to_openbabel()).strip()


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
        <https://github.com/dudektria/%(prog)s>""",
    )

    parser.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help="create a simple boilerplate input template for you to modify",
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s {:s}".format(__version__)
    )

    parser.add_argument(
        "template",
        metavar="template.package.ext | template.ext",
        help="""template file.
        "ext" can be anything.
        "package" might be one of the following:
        {}.""".format(
            ", ".join(REPOSITORY.keys())
        ),
    )
    parser.add_argument(
        "descriptors",
        metavar="descriptor.ext",
        nargs="*",
        help="""files describing molecules, which are read using Open Babel
        (run "$ obabel -L formats" for a list of all available file
        formats).""",
    )

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
            input_prefix, description_extension = os.path.splitext(descriptor)

            try:
                molecule = Atoms(cclib.ccopen(descriptor).parse())
            except KeyError:
                molecule = Atoms(
                    cclib.bridge.cclib2openbabel.readfile(
                        descriptor, description_extension[1:]
                    )
                )

            if not molecule.name:
                molecule.name = descriptor

            written_files = pnictogen(molecule, input_prefix, args.template, extension)

            for written_file in written_files:
                print("{:s} written".format(written_file))


def pnictogen(molecule, input_prefix, template, extension=None, **kwargs):
    """
    Generate inputs based on a template and a collection of molecules.

    Parameters
    ----------
    molecule : ccData-like
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

    Extra named arguments are passed directly to the template

    Returns
    -------
    written_files : list of str
        A list of paths to generated input files

    Examples
    --------
    This is the function you would call from within Python code. A simple
    example of use would be:

    >>> mol = Atoms(cclib.bridge.cclib2openbabel.readfile("data/co.xyz", "xyz"))
    >>> pnictogen(mol, "data/co", "pnictogen/repo/ORCA.inp")
    ['data/co.inp']

    """
    if extension is None:
        package, extension = os.path.basename(template).split(".")[-2:]

    written_files = []

    raw_rendered = render_template(
        template, input_prefix=input_prefix, molecule=molecule, **kwargs
    )

    at_id = None
    raw_rendered = raw_rendered.split("--@")
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
    ...     "molecule": Atoms(cclib.bridge.cclib2openbabel.readfile("data/water.xyz", "xyz"))
    ... }
    >>> context["molecule"].name = "data/water.xyz"
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
    extensions = kwargs.pop("extensions", [])

    jinja_env = Environment(
        loader=FileSystemLoader("./"), extensions=extensions, trim_blocks=True
    )
    jinja_env.globals.update({"import": importlib.import_module})

    try:
        template_jinja = jinja_env.get_template(template)
    except TemplateNotFound:
        template_jinja = jinja_env.from_string(open(template).read())

    return template_jinja.render(kwargs)


if __name__ == "__main__":
    main()
