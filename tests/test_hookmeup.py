# -*- coding: utf-8 -*-

"""Tests for hookmeup package."""
from __future__ import print_function
import os
import subprocess
from subprocess import CalledProcessError

import pytest
import hookmeup
from hookmeup.hookmeup import HookMeUpError, _DjangoMigrator

# pylint: disable=protected-access
@pytest.fixture
def mock_install(mocker):
    """Mock low-level API's called by install"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value='.git')
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
    mock_file.assert_called_once_with(
            os.path.sep.join(['.git', 'hooks', 'post-checkout']),
            'w'
            )
    mock_file().write.assert_called_once_with(
            '#!/bin/sh\nhookmeup post-checkout "$@"\n'
            )
    os.path.exists.assert_called_once_with(
            os.path.sep.join(['.git', 'hooks', 'post-checkout'])
            )

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
    os.path.exists.assert_called_once_with(
            os.path.sep.join(['.git', 'hooks', 'post-checkout'])
            )

def test_install_bad_arg(mocker):
    """Test install function when arg inappropriately provided"""
    with pytest.raises(HookMeUpError):
        hookmeup.hookmeup.install({'oops': 'don\t do this'})

def test_install_outside_repo(mocker):
    """Test install outside of Git repository"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.Mock(
                    side_effect=CalledProcessError(returncode=1, cmd='cmd')
                    )
            )
    with pytest.raises(HookMeUpError):
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
        raise HookMeUpError('test error')
    except HookMeUpError as error:
        assert str(error) == 'hookmeup: test error'

def test_post_checkout_non_branch(mocker):
    """Test post_checkout call for non-branch checkout"""
    mocker.patch(
            'hookmeup.hookmeup._adjust_pipenv'
            )
    mocker.patch.object(
            _DjangoMigrator,
            'migrations_changed'
            )
    hookmeup.hookmeup.post_checkout(
            {'old': 'old',
             'new': 'new',
             'branch_checkout': 0}
            )
    hookmeup.hookmeup._adjust_pipenv.assert_not_called()
    _DjangoMigrator.migrations_changed.assert_not_called()

def test_post_checkout(mocker):
    """Test nominal post_checkout"""
    migration = os.path.sep.join(['app1', 'migrations', '0003_test.py'])
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value='M \
                    Pipfile\nA '
                    + migration)
            )
    mocker.patch('hookmeup.hookmeup._adjust_pipenv')
    hookmeup.hookmeup.post_checkout({
            'branch_checkout': 1,
            'old': 'HEAD^',
            'new': 'HEAD'
            })
    assert subprocess.check_output.call_count == 3
    hookmeup.hookmeup._adjust_pipenv.assert_called_once()

def test_post_checkout_no_changes(mocker):
    """Test nominal post_checkout"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value='')
            )
    mocker.patch('hookmeup.hookmeup._adjust_pipenv')
    hookmeup.hookmeup.post_checkout({
            'branch_checkout': 1,
            'old': 'HEAD^',
            'new': 'HEAD'
            })
    assert subprocess.check_output.call_count == 2
    assert hookmeup.hookmeup._adjust_pipenv.call_count == 0

def test__adjust_pipenv(mocker):
    """Test call to _adjust_pipenv"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value='.git\n')
            )
    hookmeup.hookmeup._adjust_pipenv()
    assert subprocess.check_output.call_count == 2

def test__adjust_pipenv_failure(mocker):
    """Test _adjust_pipenv with failed subprocess call"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.Mock(
                    side_effect=CalledProcessError(returncode=1, cmd='cmd')
                    )
            )
    with pytest.raises(HookMeUpError):
        hookmeup.hookmeup._adjust_pipenv()

def build_diff_output(file_list):
    lines = []
    for diff_file in file_list:
        lines.append(
                diff_file[0] + '    ' + os.path.sep.join(diff_file[1:])
                )
    return '\n'.join(lines)

def test_migrate_up(mocker):
    """Test a nominal Django migration"""
    file_list = [['A', 'app1', 'migrations', '0002_auto.py'],
                 ['A', 'app2', 'migrations', '0003_test.py'],
                 ['A', 'other_file.py']
                ]
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value=build_diff_output(file_list))
            )
    migrator = _DjangoMigrator({'old': 'test', 'new': 'test2'})
    assert migrator.migrations_changed() is True
    subprocess.check_output.assert_called_once()
    mocker.resetall()
    migrator.migrate()
    subprocess.check_output.assert_called_once_with(
            migrator._migrate_command + ['app1', 'app2'], text=True
            )

def test_migrate_down(mocker):
    """Test a nominal Django migration downgrade"""
    file_list = [['D', 'app1', 'migrations', '0002_auto.py'],
                 ['D', 'app2', 'migrations', '0003_test.py'],
                 ['A', 'other_file.py']
                ]
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value=build_diff_output(file_list))
            )
    migrator = _DjangoMigrator({'old': 'test', 'new': 'test2'})
    assert migrator.migrations_changed() is True
    subprocess.check_output.assert_called_once()
    mocker.resetall()
    migrator.migrate()
    assert subprocess.check_output.call_count == 2
    subprocess.check_output.assert_any_call(
            migrator._migrate_command + ['app1', '0001'], text=True
            )
    subprocess.check_output.assert_any_call(
            migrator._migrate_command + ['app2', '0002'], text=True
            )

def test_migrate_to_zero(mocker):
    """Test a Django migration upgrade with an intervening squash"""
    file_list = [['A', 'app1', 'migrations', '0002_auto.py'],
                 ['A', 'app2', 'migrations', '0003_test.py'],
                 ['D', 'app3', 'migrations', '0001_initial.py'],
                 ['D', 'app3', 'migrations', '0002_auto.py'],
                 ['A', 'app3', 'migrations', '0001_squashed.py'],
                 ['A', 'other_file.py']
                ]
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value=build_diff_output(file_list))
            )
    migrator = _DjangoMigrator({'old': 'test', 'new': 'test2'})
    assert migrator.migrations_changed() is True
    subprocess.check_output.assert_called_once()
    mocker.resetall()
    migrator.migrate()
    assert subprocess.check_output.call_count == 2
    subprocess.check_output.assert_any_call(
            migrator._migrate_command + ['app3', 'zero'], text = True
            )
    subprocess.check_output.assert_any_call(
            migrator._migrate_command + ['app1', 'app2', 'app3'], text = True
            )

def test_remove(mocker):
    """Test removing the hook (nominal case)"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value='.git\n')
            )
    mocker.patch(
            'os.path.exists',
            new=mocker.MagicMock(return_value=True)
            )
    mock_file = mocker.mock_open(
            read_data='#!/bin/sh\nfoo\nhookmeup post-checkout "$@"'
            )
    mocker.patch('hookmeup.hookmeup.open', new=mock_file)
    hookmeup.hookmeup.remove({})
    subprocess.check_output.assert_called_once()
    os.path.exists.assert_called_once()
    assert mock_file.call_count == 2
    mock_file().read.assert_called_once()
    mock_file().writelines.assert_called_with(['#!/bin/sh\n', 'foo\n'])

def test_remove_no_repo(mocker):
    """Test removing the hook (nominal case)"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.Mock(
                    side_effect=CalledProcessError(128, 'cmd'))
            )
    mocker.patch(
            'os.path.exists',
            new=mocker.MagicMock(return_value=False)
            )
    mock_file = mocker.mock_open(
            read_data='#!/bin/sh\nfoo\nhookmeup post-checkout "$@"'
            )
    mocker.patch('hookmeup.hookmeup.open', new=mock_file)
    with pytest.raises(HookMeUpError):
        hookmeup.hookmeup.remove({})
    subprocess.check_output.assert_called_once()
    assert os.path.exists.call_count == 0
    assert mock_file.call_count == 0
    assert mock_file().read.call_count == 0
    assert mock_file().writelines.call_count == 0

def test_remove_no_hook_file(mocker):
    """Test remove when no hook file"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value='.git\n')
            )
    mocker.patch(
            'os.path.exists',
            new=mocker.MagicMock(return_value=False)
            )
    mock_file = mocker.mock_open(
            read_data='#!/bin/sh\nfoo\nhookmeup post-checkout "$@"'
            )
    mocker.patch('hookmeup.hookmeup.open', new=mock_file)
    mocker.patch('hookmeup.hookmeup.print')
    hookmeup.hookmeup.remove({})
    subprocess.check_output.assert_called_once()
    os.path.exists.assert_called_once()
    assert mock_file.call_count == 0
    assert mock_file().read.call_count == 0
    hookmeup.hookmeup.print.assert_called_with(
            'hookmeup: no hook to remove'
            )
    assert mock_file().writelines.call_count == 0

def test_remove_not_installed(mocker):
    """Test remove when hook not installed"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value='.git\n')
            )
    mocker.patch(
            'os.path.exists',
            new=mocker.MagicMock(return_value=True)
            )
    mock_file = mocker.mock_open(
            read_data='#!/bin/sh\nfoo'
            )
    mocker.patch('hookmeup.hookmeup.open', new=mock_file)
    mocker.patch('hookmeup.hookmeup.print')
    hookmeup.hookmeup.remove({})
    subprocess.check_output.assert_called_once()
    os.path.exists.assert_called_once()
    mock_file.assert_called_once()
    mock_file().read.assert_called_once()
    hookmeup.hookmeup.print.assert_called_with(
            'hookmeup: hookmeup not installed. nothing to do.'
            )
    assert mock_file().writelines.call_count == 0

def test_remove_unexpected_arg(mocker):
    """Test remove when hook not installed"""
    with pytest.raises(HookMeUpError):
        hookmeup.hookmeup.remove({'this': 'that'})
