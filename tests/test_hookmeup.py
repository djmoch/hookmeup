# -*- coding: utf-8 -*-

"""Tests for hookmeup package."""
import os
import subprocess
from subprocess import CalledProcessError

import pytest
import hookmeup
from hookmeup.hookmeup import HookMeUpError, DjangoMigrator

# pylint: disable=protected-access
@pytest.fixture
def mock_install(mocker):
    """Mock low-level API's called by install"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value=b'.git')
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
    assert hookmeup.hookmeup.print.call_count == 1

def test_error():
    """Test accessing error members"""
    try:
        raise HookMeUpError('test error')
    except HookMeUpError as error:
        assert str(error) == 'hookmeup: test error'

def test_post_checkout_non_branch(mocker):
    """Test post_checkout call for non-branch checkout"""
    mocker.patch(
            'hookmeup.hookmeup.adjust_pipenv'
            )
    mocker.patch.object(
            DjangoMigrator,
            'migrations_changed'
            )
    hookmeup.hookmeup.post_checkout(
            {'old': 'old',
             'new': 'new',
             'branch_checkout': 0}
            )
    hookmeup.hookmeup.adjust_pipenv.assert_not_called()
    DjangoMigrator.migrations_changed.assert_not_called()

def test_post_checkout(mocker):
    """Test nominal post_checkout"""
    migration = bytes(
            os.path.sep.join(['app1', 'migrations', '0003_test.py']),
            'utf-8'
            )
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value=b'M \
                    Pipfile\nA '
                    + migration)
            )
    mocker.patch('hookmeup.hookmeup.adjust_pipenv')
    hookmeup.hookmeup.post_checkout({
            'branch_checkout': 1,
            'old': 'HEAD^',
            'new': 'HEAD'
            })
    assert subprocess.check_output.call_count == 3
    assert hookmeup.hookmeup.adjust_pipenv.call_count == 1

def test_post_checkout_no_changes(mocker):
    """Test nominal post_checkout"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value=b'')
            )
    mocker.patch('hookmeup.hookmeup.adjust_pipenv')
    hookmeup.hookmeup.post_checkout({
            'branch_checkout': 1,
            'old': 'HEAD^',
            'new': 'HEAD'
            })
    assert subprocess.check_output.call_count == 2
    assert hookmeup.hookmeup.adjust_pipenv.call_count == 0

def test_adjust_pipenv(mocker):
    """Test call to adjust_pipenv"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value=b'.git\n')
            )
    hookmeup.hookmeup.adjust_pipenv()
    assert subprocess.check_output.call_count == 2

def test_adjust_pipenv_failure(mocker):
    """Test adjust_pipenv with failed subprocess call"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.Mock(
                    side_effect=CalledProcessError(returncode=1, cmd='cmd')
                    )
            )
    with pytest.raises(HookMeUpError):
        hookmeup.hookmeup.adjust_pipenv()

def build_diff_output(file_list):
    lines = []
    for diff_file in file_list:
        lines.append(
                diff_file[0] + '    ' + os.path.sep.join(diff_file[1:])
                )
    print(lines)
    return bytes('\n'.join(lines), 'utf-8')

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
    migrator = DjangoMigrator({'old': 'test', 'new': 'test2'})
    assert migrator.migrations_changed() is True
    assert subprocess.check_output.call_count == 1
    mocker.resetall()
    migrator.migrate()
    subprocess.check_output.assert_called_once_with(
            migrator._migrate_command + ['app1', 'app2']
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
    migrator = DjangoMigrator({'old': 'test', 'new': 'test2'})
    assert migrator.migrations_changed() is True
    assert subprocess.check_output.call_count == 1
    mocker.resetall()
    migrator.migrate()
    assert subprocess.check_output.call_count == 2
    subprocess.check_output.assert_any_call(
            migrator._migrate_command + ['app1', '0001']
            )
    subprocess.check_output.assert_any_call(
            migrator._migrate_command + ['app2', '0002']
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
    migrator = DjangoMigrator({'old': 'test', 'new': 'test2'})
    assert migrator.migrations_changed() is True
    assert subprocess.check_output.call_count == 1
    mocker.resetall()
    migrator.migrate()
    assert subprocess.check_output.call_count == 2
    subprocess.check_output.assert_any_call(
            migrator._migrate_command + ['app3', 'zero']
            )
    subprocess.check_output.assert_any_call(
            migrator._migrate_command + ['app1', 'app2', 'app3']
            )

def test_remove(mocker):
    """Test removing the hook (nominal case)"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value=b'.git\n')
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
    assert subprocess.check_output.call_count == 1
    assert os.path.exists.call_count == 1
    assert mock_file.call_count == 2
    assert mock_file().read.call_count == 1
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
    assert subprocess.check_output.call_count == 1
    assert os.path.exists.call_count == 0
    assert mock_file.call_count == 0
    assert mock_file().read.call_count == 0
    assert mock_file().writelines.call_count == 0

def test_remove_no_hook_file(mocker):
    """Test remove when no hook file"""
    mocker.patch(
            'subprocess.check_output',
            new=mocker.MagicMock(return_value=b'.git\n')
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
    assert subprocess.check_output.call_count == 1
    assert os.path.exists.call_count == 1
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
            new=mocker.MagicMock(return_value=b'.git\n')
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
    assert subprocess.check_output.call_count == 1
    assert os.path.exists.call_count == 1
    assert mock_file.call_count == 1
    assert mock_file().read.call_count == 1
    hookmeup.hookmeup.print.assert_called_with(
            'hookmeup: hookmeup not installed. nothing to do.'
            )
    assert mock_file().writelines.call_count == 0

def test_remove_unexpected_arg(mocker):
    """Test remove when hook not installed"""
    with pytest.raises(HookMeUpError):
        hookmeup.hookmeup.remove({'this': 'that'})
