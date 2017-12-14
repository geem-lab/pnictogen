#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from glob import glob
from pnictogen import argparser, main

example_templates = glob(os.path.join(os.path.dirname(__file__),
                                      "../examples/templates/*"))
example_xyz_files = glob(os.path.join(os.path.dirname(__file__),
                                      "../examples/*.xyz"))


def test_argparser():
    argv = ["my_template.GAMESS.inp", "one.xyz", "two.pdb", "three.mop"]

    parser = argparser()
    parser.parse_args(argv)


def test_main_for_template_generation():
    for template in example_templates:
        main([template, "-g"])


def test_main_with_xyz_files():
    for template in example_templates:
        # One at a time
        for xyz_file in example_xyz_files:
            main([template, xyz_file])

        # All at once
        main([template] + list(example_xyz_files))
