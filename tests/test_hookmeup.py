# -*- coding: utf-8 -*-

"""Tests for `hookmeup` package."""
import os
import subprocess

import pytest
import hookmeup

@pytest.fixture
def mock_install(mocker):
    """Mock low-level API's called by install"""
    completed_process = subprocess.CompletedProcess(
            args=['git', 'rev-parse', '--git-dir'],
            returncode=0,
            stdout=b'.git',
            stderr=b''
            )
    mocker.patch(
            'subprocess.run',
            new=mocker.MagicMock(return_value=completed_process)
            )

def test_install(mock_install, mocker):
    """Test install function"""
    mock_file = mocker.mock_open()
    mocker.patch('hookmeup.hookmeup.open', mock_file)
    mocker.patch(
            'os.path.exists',
            new=mocker.MagicMock(return_value=False)
            )
    hookmeup.hookmeup.install({})
    mock_file.assert_called_once_with('.git/hooks/post-checkout', 'w')
    mock_file().write.assert_called_once_with(
            '#!/bin/sh\nhookmeup post-checkout "$@"\n'
            )
    os.path.exists.assert_called_once_with('.git/hooks/post-checkout')

def test_install_existing_hook(mock_install, mocker):
    """Test install function when post-checkout already exists"""
    mock_file = mocker.mock_open()
    mocker.patch('hookmeup.hookmeup.open', mock_file)
    mocker.patch(
            'os.path.exists',
            new=mocker.MagicMock(return_value=True)
            )
    hookmeup.hookmeup.install({})
    assert mock_file.call_count == 2
    os.path.exists.assert_called_once_with('.git/hooks/post-checkout')

def test_install_bad_arg(mocker):
    """Test install function when arg inappropriately provided"""
    with pytest.raises(hookmeup.hookmeup.HookMeUpError):
        hookmeup.hookmeup.install({'oops': 'don\t do this'})

def test_install_outside_repo(mocker):
    """Test install outside of Git repository"""
    completed_process = subprocess.CompletedProcess(
            args=['git', 'rev-parse', '--git-dir'],
            returncode=128,
            stdout=b'',
            stderr=b'fatal: not a git repository'
            )
    mocker.patch(
            'subprocess.run',
            new=mocker.MagicMock(return_value=completed_process)
            )
    with pytest.raises(hookmeup.hookmeup.HookMeUpError):
        hookmeup.hookmeup.install({})

def test_install_already_installed(mock_install, mocker):
    """Test attempt to install when hook already installed"""
    mock_file = mocker.mock_open(
            read_data='#!/bin/sh\nhookmeup post-checkout\n'
            )
    mocker.patch('hookmeup.hookmeup.open', mock_file)
    mocker.patch(
            'os.path.exists',
            new=mocker.MagicMock(return_value=True)
            )
    mocker.patch('hookmeup.hookmeup.print')
    hookmeup.hookmeup.install({})
    hookmeup.hookmeup.print.assert_called_once()

def test_error():
    """Test accessing error members"""
    try:
        raise hookmeup.hookmeup.HookMeUpError('test error')
    except hookmeup.hookmeup.HookMeUpError as error:
        assert str(error) == 'hookmeup: test error'

def test_post_checkout(mocker):
    """Test nominal post_checkout"""
    completed_process = subprocess.CompletedProcess(
            args=['git',
                  'diff',
                  '--name-status',
                  'HEAD^',
                  'HEAD',
                  '--',
                  'Pipfile'],
            returncode=0,
            stdout=b'M   Pipfile\n',
            stderr=b''
            )
    mocker.patch(
            'subprocess.run',
            new=mocker.MagicMock(return_value=completed_process)
            )
    mocker.patch('hookmeup.hookmeup.adjust_pipenv')
    hookmeup.hookmeup.post_checkout({
            'branch_checkout': 1,
            'old': 'HEAD^',
            'new': 'HEAD'
            })
    subprocess.run.assert_called_once()
    hookmeup.hookmeup.adjust_pipenv.assert_called_once()

def test_post_checkout_no_changes(mocker):
    """Test nominal post_checkout"""
    completed_process = subprocess.CompletedProcess(
            args=['git',
                  'diff',
                  '--name-status',
                  'HEAD^',
                  'HEAD',
                  '--',
                  'Pipfile'],
            returncode=0,
            stdout=b'\n',
            stderr=b''
            )
    mocker.patch(
            'subprocess.run',
            new=mocker.MagicMock(return_value=completed_process)
            )
    mocker.patch('hookmeup.hookmeup.adjust_pipenv')
    hookmeup.hookmeup.post_checkout({
            'branch_checkout': 1,
            'old': 'HEAD^',
            'new': 'HEAD'
            })
    subprocess.run.assert_called_once()
    assert hookmeup.hookmeup.adjust_pipenv.call_count == 0

def test_adjust_pipenv(mocker):
    """Test call to adjust_pipenv"""
    completed_process = subprocess.CompletedProcess(
            args=['pipenv', 'clean'],
            returncode=0,
            stdout=b'.git',
            stderr=b''
            )
    mocker.patch(
            'subprocess.run',
            new=mocker.MagicMock(return_value=completed_process)
            )
    hookmeup.hookmeup.adjust_pipenv()
    assert subprocess.run.call_count == 2

def test_adjust_pipenv_failure(mocker):
    """Test adjust_pipenv with failed subprocess call"""
    completed_process = subprocess.CompletedProcess(
            args=['pipenv', 'clean'],
            returncode=1,
            stdout=b'.git',
            stderr=b''
            )
    mocker.patch(
            'subprocess.run',
            new=mocker.MagicMock(return_value=completed_process)
            )
    with pytest.raises(hookmeup.hookmeup.HookMeUpError):
        hookmeup.hookmeup.adjust_pipenv()

def test_migrate_up(mocker):
    """Test a nominal Django migration"""
    completed_process = subprocess.CompletedProcess(
            args=['git', 'diff', '--name-status'],
            returncode=0,
            stdout=b'\
                    A    app1/migrations/0002_auto.py\n\
                    A    app2/migrations/0003_test.py\n\
                    A    other_file.py\n',
            stderr=b''
            )
    mocker.patch(
            'subprocess.run',
            new=mocker.MagicMock(return_value=completed_process)
            )

def test_migrate_down(mocker):
    """Test a nominal Django migration downgrade"""
    completed_process = subprocess.CompletedProcess(
            args=['git', 'diff', '--name-status'],
            returncode=0,
            stdout=b'\
                    D    app1/migrations/0002_auto.py\n\
                    D    app2/migrations/0003_test.py\n\
                    A    other_file.py\n',
            stderr=b''
            )
    mocker.patch(
            'subprocess.run',
            new=mocker.MagicMock(return_value=completed_process)
            )

def test_squashed_migrate_up(mocker):
    """Test a Django migration upgrade with an intervening squash"""
    completed_process = subprocess.CompletedProcess(
            args=['git', 'diff', '--name-status'],
            returncode=0,
            stdout=b'\
                    A    app1/migrations/0002_auto.py\n\
                    A    app2/migrations/0003_test.py\n\
                    D    app3/migrations/0001_initial.py\n\
                    D    app3/migrations/0002_auto.py\n\
                    A    app3/migrations/0001_squashed.py\n\
                    A    other_file.py\n',
            stderr=b''
            )
    mocker.patch(
            'subprocess.run',
            new=mocker.MagicMock(return_value=completed_process)
            )

def test_squashed_migrate_down(mocker):
    """Test a Django migration downgrade with an intervening squash"""
    completed_process = subprocess.CompletedProcess(
            args=['git', 'diff', '--name-status'],
            returncode=0,
            stdout=b'\
                    A    app1/migrations/0002_auto.py\n\
                    A    app2/migrations/0003_test.py\n\
                    A    app3/migrations/0001_initial.py\n\
                    A    app3/migrations/0002_auto.py\n\
                    D    app3/migrations/0001_squashed.py\n\
                    A    other_file.py\n',
            stderr=b''
            )
    mocker.patch(
            'subprocess.run',
            new=mocker.MagicMock(return_value=completed_process)
            )
