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
    def __init__(self, args):
        self.added_migration_apps = []
        self.oldest_deleted = {}
        self._migrate_command = ['pipenv',
                                 'run',
                                 'python',
                                 'manage.py',
                                 'migrate']
        deleted_migrations = {}
        stdout = call_checked_subprocess(
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
            call_checked_subprocess(
                    self._migrate_command + [app, target_migration],
                    'rollback migration for {} failed'.format(app)
                    )

        if self.added_migration_apps != []:
            call_checked_subprocess(
                    self._migrate_command + self.added_migration_apps,
                    'migration failed'
                    )

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
    migrator = DjangoMigrator(args)
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
