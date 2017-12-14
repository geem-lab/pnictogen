#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import openbabel as ob
from subprocess import call
from tempfile import mkstemp
from mendeleev import element

_obconv = ob.OBConversion()
_obbuild = ob.OBBuilder()
supported_extensions_dict = dict([fmt.split(" -- ") for fmt
                                  in _obconv.GetSupportedInputFormat()])


def read_molecules(filepath, informat=None):
    """
    Read a file with probably many molecules and return a list of them

    Parameters
    ----------
    filepath : str
    informat : str, optional
        This tells the format of the file (it will be guessed by the file
        extension if not provided). This should be a file format supported by
        Open Babel.

    Returns
    -------
    list of Molecule
    """
    if informat is None:
        basename, molecule_extension = os.path.splitext(filepath)
        informat = molecule_extension[1:]
    _obconv.SetInFormat(informat)

    molecules = []

    obmol = ob.OBMol()
    not_finished = _obconv.ReadFile(obmol, filepath)
    while not_finished:
        molecules.append(Molecule(obmol))

        obmol = ob.OBMol()
        not_finished = _obconv.Read(obmol)

    return molecules


class Atom(object):
    """
    Abstraction for atoms

    Parameters
    ----------
    source : openbabel.OBAtom

    Examples
    --------
    Periodic table properties are available through `mendeleev`:

    >>> from pnictogen.molecule import Molecule
    >>> mol = Molecule("C#O")
    >>> for atom in mol:
    ...     (atom.name, atom.en_pauling, atom.vdw_radius)
    (u'Carbon', 2.55, 170.0)
    (u'Oxygen', 3.44, 152.0)
    """

    def __init__(self, source):
        self.OBAtom = source

    def __getattr__(self, attr):
        return getattr(element(self.atomic_number), attr)

    @property
    def atomic_number(self):
        """
        Return atomic number

        Returns
        -------
        int
        """
        return self.OBAtom.GetAtomicNum()

    @property
    def coords(self):
        """
        Return cartesian coordinates

        Returns
        -------
        numpy.array
        """
        return np.array([self.OBAtom.GetX(),
                         self.OBAtom.GetY(),
                         self.OBAtom.GetZ()])


class Molecule(object):
    """
    Abstraction for molecules

    Parameters
    ----------
    source : openbabel.OBMol or str
        This might be either an Open Babel object representing a molecule or
        the content of a file type Open Babel is able to read.
    informat : str, optional
        This tells the format of source if source is a string. This should be a
        file format supported by Open Babel.

    Examples
    --------
    Molecules can be obtained from any format handled by Open Babel:

    >>> from pnictogen.molecule import Molecule
    >>> mol = Molecule("1\\nHydrogen\\nH\\t0.0 0.0 0.0", "xyz")
    >>> mol.charge, mol.spin, mol.title
    (0, 2, 'Hydrogen')

    Reading a molecule from a file is easy:

    >>> with open("examples/water.xyz") as stream:
    ...     mol = Molecule(stream.read(), "xyz")
    >>> mol.title
    'PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2'

    When you iterate over a molecule, you're actually iterating over its atoms,
    as follows:

    >>> mol = Molecule("CCC")
    >>> n_el = 0
    >>> for atom in mol:
    ...    n_el += atom.atomic_number
    >>> print(n_el)
    18
    """

    def __init__(self, source, informat="can"):
        if isinstance(source, ob.OBMol):
            self.OBMol = source
        else:
            _obconv.SetInFormat(informat)

            self.OBMol = ob.OBMol()
            _obconv.ReadString(self.OBMol, source)

        # If no title, use canonical SMILES
        if self.title.strip() == "":
            self.title = self.write("can")

    def __iter__(self):
        return iter(self.atoms)

    def addh(self):
        """
        Add hydrogens
        """
        self.OBMol.AddHydrogens()

    @property
    def atoms(self):
        """
        Return a list of atoms

        Returns
        -------
        list of Atom
        """
        return [Atom(self.OBMol.GetAtom(i + 1))
                for i in range(self.OBMol.NumAtoms())]

    def _getcharge(self):
        """
        Return total charge

        Returns
        -------
        int
        """
        return self.OBMol.GetTotalCharge()

    def _setcharge(self, new_charge):
        """
        Set a new total charge

        Parameters
        ----------
        new_charge : int
        """
        return self.OBMol.SetTotalCharge(new_charge)

    charge = property(_getcharge, _setcharge)

    def conformers(self, nconf=30, children=5, mutability=5, converge=25,
                   score="rmsd", useformat="xyz"):
        """
        Conformer search provided by Open Babel based on a genetic algorithm.
        You might want to play around with the parameters for this function
        (see below).

        Parameters
        ----------
        nconf : int, optional
            Number of conformers to generate. Some suggested values
            (doi:10.1021/ci2004658):
            * 50 if number of rotatable bonds is less than 7 (default)
            * 200 if this number is between 8 and 12
            * 300 otherwise
        children : int, optional
            Number of children to generate for each parent
        mutability : int, optional
            Mutation frequency (e.g. 5 means 1/5 bonds are permuted, 10 means
            1/10).
        converge : int, optional
            Number of identical generations before convergence is reached
        score : str, optional
            Scoring function ("rmsd" or "energy")
        useformat : str, optional
            File format to be used internally

        Returns
        -------
        list of Molecule

        Examples
        --------

        The number of conformers found will depend on the number of rotatable
        bonds in the molecule:

        >>> for i in range(1, 8):
        ...     smi = "C" * i
        ...     mol = Molecule(smi)
        ...     nconf = len(mol.conformers(100))
        ...     print("Found {:2d} conformers for {:s}".format(nconf, smi))
        Found  1 conformers for C
        Found  1 conformers for CC
        Found  1 conformers for CCC
        Found  3 conformers for CCCC
        Found  9 conformers for CCCCC
        Found 27 conformers for CCCCCC
        Found 79 conformers for CCCCCCC
        """

        if self.dim != 3:
            self.make3D()

        # I believe OBConformerSearch has no Python interface yet, so we call
        # Open Babel here in shell.
        infile, infile_name = mkstemp(suffix=".{}".format(useformat))
        os.write(infile, self.write(useformat))

        basename = os.path.split(infile_name)
        outfile_name = os.path.join(basename[0],
                                    "{}{}".format("ga_", basename[1]))

        # You need to have 3D coordinates for this to work
        call(["obabel", infile_name, "-O", outfile_name, "--conformer",
              "--nconf", str(nconf), "--children", str(children),
              "--mutability", str(mutability),  "--converge", str(converge),
              "--score", score, "--writeconformers"])

        return read_molecules(outfile_name)

    @property
    def dim(self):
        """
        Dimensionality of coordinates (2D, 3D or 0D)

        Returns
        -------
        int
        """
        return self.OBMol.GetDimension()

    def make3D(self):
        """
        Generate 3D coordinates and add hydrogens
        """
        _obbuild.Build(self.OBMol)
        self.addh()

    def _getspin(self):
        """
        Return total spin multiplicity

        Returns
        -------
        int
        """
        return self.OBMol.GetTotalSpinMultiplicity()

    def _setspin(self, new_spin):
        """
        Set a new total spin multiplicity

        Parameters
        ----------
        new_spin : int
        """
        return self.OBMol.SetTotalSpinMultiplicity(new_spin)

    spin = property(_getspin, _setspin)

    def _gettitle(self):
        """
        Return the title of the molecule

        Returns
        -------
        str
        """
        return self.OBMol.GetTitle()

    def _settitle(self, new_title):
        """
        Set a new title for the molecule

        Parameters
        ----------
        new_title : str
        """
        self.OBMol.SetTitle(new_title)

    title = property(_gettitle, _settitle)

    def write(self, outformat="can"):
        """
        Convert molecule to a particular format, probably using Open Babel

        Parameters
        ----------
        outformat : str, optional
            Format to write the molecule to. All formats supported by Open
            Babel can be used, plus a few ones:
            * "simplexyz": one atom per line as in "xyz" format
            * "simplemop": same as "simplexyz" but for "mop"

        Returns
        -------
        str
            A string representing the converted molecule

        Examples
        --------
        This function can be used as follows:

        >>> from pnictogen.molecule import Molecule
        >>> with open("examples/water.xyz") as stream:
        ...     Molecule(stream.read(), "xyz").write()
        'O\\tPBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2\\n'

        A molecule can be written in a specified format:

        >>> with open("examples/water.xyz") as stream:
        ...     mol = Molecule(stream.read(), "xyz")
        ...     print("When the coordinates...")
        ...     print(mol.write("simplexyz"))
        ...     print("...receive optimization flags you get...")
        ...     print(mol.write("simplemop"))
        When the coordinates...
        O          0.05840        0.05840        0.00000
        H          1.00961       -0.06802        0.00000
        H         -0.06802        1.00961        0.00000
        ...receive optimization flags you get...
        O   0.05840 1  0.05840 1  0.00000 1
        H   1.00961 1 -0.06802 1  0.00000 1
        H  -0.06802 1  1.00961 1  0.00000 1
        """

        if outformat == "simplexyz":
            _obconv.SetOutFormat("xyz")
            converted = _obconv.WriteString(self.OBMol)
            converted = converted.split("\n", 2)[2].strip()
        elif outformat == "simplemop":
            _obconv.SetOutFormat("mop")
            converted = _obconv.WriteString(self.OBMol)
            converted = converted.split("\n", 2)[2].strip()
        else:
            _obconv.SetOutFormat(outformat)
            converted = _obconv.WriteString(self.OBMol)

        return converted
