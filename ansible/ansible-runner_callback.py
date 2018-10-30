#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import json
from collections import namedtuple

from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase


class ResultCallback(CallbackBase):

    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        super(ResultCallback, self).v2_runner_on_unreachable(result)
        print(json.dumps({result._host.name: result._result}, indent=4))

    def v2_runner_on_ok(self, result, **kwargs):
        super(ResultCallback, self).v2_runner_on_ok(result)
        print(json.dumps({result._host.name: result._result}, indent=4))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        super(ResultCallback, self).v2_runner_on_failed(result)
        print(json.dumps({result._host.name: result._result}, indent=4))


def main():
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources='./hosts')
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    playbook_path = './command.yml'

    if not os.path.exists(playbook_path):
        print('[INFO] The playbook does not exist')
        sys.exit()

    Options = namedtuple(
        'Options',
        ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path', 'forks',
         'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
         'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check', 'diff']
    )
    options = Options(
        listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
        module_path=None, forks=100, remote_user='root', private_key_file=None,
        ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True,
        become_method='sudo', become_user='root', verbosity=None, check=False, diff=False
    )

    variable_manager.extra_vars = {'hoge': 'mywebserver'}
    passwords = {}

    executor = PlaybookExecutor(
        playbooks=[playbook_path],
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        options=options,
        passwords=passwords
    )
    results_callback = ResultCallback()
    executor._tqm._stdout_callback = results_callback
    results = executor.run()


if __name__ == '__main__':
    main()
