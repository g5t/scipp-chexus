# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
import argparse
import sys

import chexus


def _is_text_file(path: str) -> bool:
    """Check if file is text file"""
    try:
        with open(path, 'r') as f:
            f.readline()
        return True
    except UnicodeDecodeError:
        return False


def main():
    parser = argparse.ArgumentParser(description='Validate NeXus files.')
    parser.add_argument(
        '--checksums', action='store_true', help='Compute and print checksums'
    )
    parser.add_argument(
        '--ignore-missing',
        action='store_true',
        help='Skip the validators that have missing dependecies',
    )
    parser.add_argument('--skip', '-S', action='append',
                        help='Skip top-level groups with name matching any provided SKIP', required=False)
    parser.add_argument('--root', '-R', action='append',
                        help='Root group(s) for checking', required=False)
    parser.add_argument('path', help='Input file')
    args = parser.parse_args()
    path = args.path
    ignore_missing = args.ignore_missing
    skip = args.skip
    root = args.root

    has_scipp = False
    try:
        import scipp  # noqa: F401
    except ModuleNotFoundError:
        if not ignore_missing:
            print(
                'Error: Scipp was not found. The Nexus file validation was not run.\n'
                'To run the full test suite you need to install scipp'
                ' using `pip install scipp` or `conda install -c scipp scipp`.'
                ' This is recommended.\n'
                'To run only the tests that don\'t require scipp and ignore this'
                ' error add the flag `--ignore-missing`.'
            )
            sys.exit(1)
    else:
        has_scipp = True

    group = chexus.read_json(path, skip=skip, root=root) if _is_text_file(path) else chexus.read_hdf5(path, skip=skip, root=root)

    validators = chexus.validators.base_validators(has_scipp=has_scipp)
    results = chexus.validate(group, validators=validators)
    print(chexus.report(results=results))
    print(chexus.make_fileinfo(path))
    if args.checksums:
        print(chexus.compute_checksum(path))


if __name__ == '__main__':
    main()
