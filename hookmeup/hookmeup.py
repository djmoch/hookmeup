# -*- coding: utf-8 -*-
"""hookmeup module."""
from __future__ import print_function
import os
import subprocess
from subprocess import CalledProcessError
import sys

FORMAT_STRING = 'hookmeup: {}'

def _print_msg(msg):
    """Print a formatted message to stdout"""
    print(FORMAT_STRING.format(msg))

class HookMeUpError(Exception):
    """Errors raised by hookmeup"""
    EXIT_CODE = 1

    def __str__(self):
        return FORMAT_STRING.format(self.args[0])

class _DjangoMigrator():
    """
    Class responsible for parsing, applying, and unapplying Django
    migrations
    """
    def __init__(self, args):
        self.added_migration_apps = []
        self.oldest_deleted = {}
        self._migrate_command = ['pipenv',
                                 'run',
                                 'python',
                                 'manage.py',
                                 'migrate']
        deleted_migrations = {}
        stdout = _call_checked_subprocess(
                ['git', 'diff', '--name-status', args['old'], args['new']],
                'not in a Git repository'
                )
        diff_lines = stdout.splitlines()
        for line in diff_lines:
            if line.find(os.path.sep + 'migrations' + os.path.sep) >= 0:
                file_status = line[0]
                file_path = line[1:-1].strip()
                file_path_segments = file_path.split(os.path.sep)
                migration_name = file_path_segments[-1].replace('.py', '')
                app_name = file_path_segments[-3]
                if file_status in ['D', 'M']:
                    if app_name not in deleted_migrations:
                        deleted_migrations[app_name] = []
                    deleted_migrations[app_name].append(migration_name)
                if file_status == 'A' \
                        and app_name not in self.added_migration_apps:
                    self.added_migration_apps.append(app_name)
        for app_name, migrations_list in deleted_migrations.items():
            migrations_list.sort()
            self.oldest_deleted[app_name] = \
                    int(migrations_list[0].split('_')[0])

    def migrations_changed(self):
        """
        Returns true if there are migrations that need to be applied
        or unapplied
        """
        return self.added_migration_apps != [] or \
                self.oldest_deleted != {}

    def migrate(self):
        """Apply/unapply any migrations as necessary"""
        for app, oldest in self.oldest_deleted.items():
            target_migration = format(oldest - 1, '04d')
            if target_migration == '0000':
                target_migration = 'zero'
            _call_checked_subprocess(
                    self._migrate_command + [app, target_migration],
                    'rollback migration for {} failed'.format(app)
                    )

        if self.added_migration_apps != []:
            _call_checked_subprocess(
                    self._migrate_command + self.added_migration_apps,
                    'migration failed'
                    )

def _call_checked_subprocess(arg_list, msg="fatal error"):
    """Handle return data from a call to a subprocess"""
    try:
        return subprocess.check_output(arg_list, text=True)
    except CalledProcessError:
        raise HookMeUpError(msg)

def _adjust_pipenv():
    """Adjust pipenv to match Pipfile"""
    _print_msg('Adjusting virtualenv to match Pipfile')
    _call_checked_subprocess(
            ['pipenv', 'clean'],
            'Attempt to clean pipenv failed'
            )

    _call_checked_subprocess(
            ['pipenv', 'sync', '--dev'],
            'Attempt to sync pipenv failed'
            )

def _pipfile_changed(args):
    """Test if the Pipfile has changed"""
    stdout = _call_checked_subprocess(
            ['git',
             'diff',
             '--name-only',
             args['old'],
             args['new'],
             '--',
             'Pipfile',
             'Pipfile.lock'],
            'Not in a Git repository'
            )

    return 'Pipfile' in str(stdout)

def post_checkout(args):
    """Run post-checkout hook"""
    if args['branch_checkout'] == 1:
        migrator = _DjangoMigrator(args)
        if migrator.migrations_changed():
            migrator.migrate()
        if _pipfile_changed(args):
            _adjust_pipenv()

def install(args):
    """Install hook into repository"""
    if args:
        raise HookMeUpError(
                "Argument passed to 'install', but expected none"
                )

    exec_name = sys.argv[0]

    stdout = _call_checked_subprocess(
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
            already_installed = exec_name in hook_file.read()

        if already_installed:
            _print_msg('already installed')
        else:
            _print_msg('installing to existing hook')
            with open(hook_path, 'a') as hook_file:
                hook_file.write(
                        '{} post-checkout "$@"\n'.format(exec_name)
                        )
    else:
        _print_msg('creating hook')
        with open(hook_path, 'w') as hook_file:
            hook_file.write(
                    '#!/bin/sh\n{} post-checkout "$@"\n'.format(exec_name)
                    )

def remove(args):
    """Remove the hook from the repository"""
    if args:
        raise HookMeUpError(
                "Argument passed to 'remove', but expected none"
                )

    exec_name = sys.argv[0]

    stdout = _call_checked_subprocess(
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
            hook_lines = hook_file.read()
            installed = exec_name in hook_lines
            hook_lines = hook_lines.splitlines()

        if installed:
            hook_lines = \
                ['{}\n'.format(line)
                 for line in hook_lines
                 if line.find(exec_name) == -1]
            with open(hook_path, 'w') as hook_file:
                hook_file.writelines(hook_lines)
        else:
            _print_msg('hookmeup not installed. nothing to do.')

    else:
        _print_msg('no hook to remove')
