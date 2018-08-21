# -*- coding: utf-8 -*-

"""A Git hook to automate your Pipenv and Django workflows"""
import argparse

from . import hookmeup

__author__ = 'Daniel Moch'
__version__ = '0.1.0'

def main():
    """Main hookmeup entrypoint"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-v', action='version',
            version='%(prog)s {}'.format(__version__))
    subparsers = parser.add_subparsers(
            title='subcommands',
            description='Valid %(prog)s subcommands')
    install_parser = subparsers.add_parser(
            'install',
            description='Run inside a repository to install the hook. \
                    Fails if the current directory is not inside a Git \
                    repository.')
    install_parser.set_defaults(func=hookmeup.install)
    post_commit_parser = subparsers.add_parser(
            'post-checkout',
            description='Run post-checkout hook. This should normally \
                    be called by Git automatically.')
    post_commit_parser.add_argument('old', help='the old commit')
    post_commit_parser.add_argument('new', help='the new commit')
    post_commit_parser.add_argument(
            'branch_checkout',
            help='1 for branch checkout, 0 otherwise')
    post_commit_parser.set_defaults(func=hookmeup.post_checkout)
    args = parser.parse_args()
    func = args.func
    arg_dict = vars(args)
    del arg_dict['func']
    func(arg_dict)
