# -*- coding: utf-8 -*-
"""hookmeup module."""
import os
import subprocess
from subprocess import CalledProcessError

class HookMeUpError(Exception):
    """Errors raised by hookmeup"""
    EXIT_CODE = 1

    def __str__(self):
        return "hookmeup: {}".format(self.args[0])

class DjangoMigrator():
    """
    Class responsible for parsing, applying, and unapplying Django
    migrations
    """
    def __init__(self):
        pass

    def migrations_changed(self):
        """
        Returns true if there are migrations that need to be applied
        or unapplied
        """
        pass

    def migrate(self):
        """Apply/unapply any migrations as necessary"""
        pass

def call_checked_subprocess(arg_list, msg="fatal error"):
    """Handle return data from a call to a subprocess"""
    try:
        return subprocess.check_output(arg_list).decode('utf-8')
    except CalledProcessError:
        raise HookMeUpError(msg)

def adjust_pipenv():
    """Adjust pipenv to match Pipfile"""
    print('Adjusting virtualenv to match Pipfile')
    call_checked_subprocess(
            ['pipenv', 'clean'],
            'Attempt to clean pipenv failed'
            )

    call_checked_subprocess(
            ['pipenv', 'sync', '--dev'],
            'Attempt to sync pipenv failed'
            )

def pipfile_changed(args):
    """Test if the Pipfile has changed"""
    stdout = call_checked_subprocess(
            ['git',
             'diff',
             '--name-status',
             args['old'],
             args['new'],
             '--',
             'Pipfile'],
            'Not in a Git repository'
            )

    return stdout.startswith('M')

def post_checkout(args):
    """Run post-checkout hook"""
    migrator = DjangoMigrator()
    if args['branch_checkout'] == 1:
        if migrator.migrations_changed():
            migrator.migrate()
        if pipfile_changed(args):
            adjust_pipenv()

def install(args):
    """Install hook into repository"""
    if len(args) is not 0:
        raise HookMeUpError(
                "Argument passed to 'install', but expected none"
                )

    stdout = call_checked_subprocess(
            ['git', 'rev-parse', '--git-dir'],
            'Not in a Git repository'
            )

    hook_path = os.path.join(
            stdout.strip(),
            'hooks',
            'post-checkout'
            )

    if os.path.exists(hook_path):
        with open(hook_path, 'r') as hook_file:
            already_installed = 'hookmeup' in hook_file.read()

        with open(hook_path, 'a') as hook_file:
            if already_installed:
                print('hookmeup already installed')
            else:
                hook_file.write('hookmeup post-checkout "$@"\n')
    else:
        with open(hook_path, 'w') as hook_file:
            hook_file.write('#!/bin/sh\nhookmeup post-checkout "$@"\n')
