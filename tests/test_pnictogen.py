#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glob import iglob

from pnictogen import argparser, main

# Only testing xyz files because I trust Open Babel
example_xyz_files = iglob("../examples/*.xyz")
example_templates = iglob("../examples/templates/*")


def test_argparser():
    for template in example_templates:
        argv = [template] + list(example_xyz_files)

        parser = argparser()
        parser.parse_args(argv)


def test_main():
    for template in example_templates:
        main(["-g", template])

    for template in example_templates:
        # One at a time
        for xyz_file in example_xyz_files:
            main([template, xyz_file])

        # All at once
        main([template] + list(example_xyz_files))


# Tests dedicated pnictogen.render_template and boilerplate templates can be
# found in test_boilerplates.py

# TODO: create hello world template in a temporary file to test
# render_template() without any molecule.
# def test_render_templates():
#     pass
