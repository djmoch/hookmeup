# -*- coding: utf-8 -*-
"""hookmeup module."""
import os
import subprocess

class HookMeUpError(Exception):
    """Errors raised by hookmeup"""
    EXIT_CODE = 1

    def __str__(self):
        return "hookmeup: {}".format(self.args[0])

def handle_completed_process(completed_process, msg="fatal error"):
    """Handle return data from a call to subprocess.run"""
    if completed_process.returncode != 0:
        raise HookMeUpError(msg)

def adjust_pipenv():
    """Adjust pipenv to match Pipfile"""
    print('Adjusting virtualenv to match Pipfile')
    completed_process = subprocess.run(
            ['pipenv', 'clean'],
            check=True
            )
    handle_completed_process(
            completed_process,
            'Attempt to clean pipenv failed'
            )

    completed_process = subprocess.run(
            ['pipenv', 'sync', '--dev'],
            check=True
            )
    handle_completed_process(
            completed_process,
            'Attempt to sync pipenv failed'
            )

def pipfile_changed(args):
    """Test if the Pipfile has changed"""
    completed_process = subprocess.run(
            ['git',
             'diff',
             '--name-status',
             args['old'],
             args['new'],
             '--',
             'Pipfile'],
            check=True,
            capture_output=True
            )
    handle_completed_process(
            completed_process,
            'Not in a Git repository'
            )

    return completed_process.stdout.decode('utf-8').startswith('M')

def post_checkout(args):
    """Run post-checkout hook"""
    if args['branch_checkout'] == 1:
        if pipfile_changed(args):
            adjust_pipenv()

def install(args):
    """Install hook into repository"""
    if len(args) is not 0:
        raise HookMeUpError(
                "Argument passed to 'install', but expected none"
                )

    completed_process = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            check=True,
            capture_output=True
            )

    handle_completed_process(
            completed_process,
            'Not in a Git repository'
            )

    hook_path = os.path.join(
            completed_process.stdout.decode('utf-8').strip(),
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
