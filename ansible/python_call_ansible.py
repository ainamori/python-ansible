#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
import shutil
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import ansible.constants as C


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


class Ansible(object):

    def play(self):
        Options = namedtuple(
            'Options',
            ['connection', 'module_path', 'forks', 'become',
             'become_method', 'become_user', 'check', 'diff', 'remote_user', 'delegate_to'])

        loader = DataLoader()
        options = Options(
            connection='paramiko',
            module_path=['/usr/share/ansible'],
            forks=10, become=None, become_method=None, become_user=None, check=False, diff=False, remote_user='root',
            delegate_to='localhost')

        passwords = dict()
        host_list = ['./hosts']

        # required for
        # https://github.com/ansible/ansible/blob/devel/lib/ansible/inventory/manager.py#L204
        if host_list:
            sources = ','.join(host_list)

        inventory = InventoryManager(loader=loader, sources=host_list)
        variable_manager = VariableManager(loader=loader, inventory=inventory)

        import yaml
        _tasks = yaml.load(open('./command.yml', 'r'))
        print(_tasks)
        tasks = [dict(action=dict(
            module='command',
            args=dict(cmd='/usr/bin/uptime')
        ))]
        print(tasks)
        play_source = dict(
            name="Ansible Play",
            hosts=['localhost'],
            gather_facts='no',
            tasks=tasks
            # tasks=[dict(action=dict(
            #     module='command',
            #     args=dict(cmd='/usr/bin/uptime')
            # ))]
        )
        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

        tqm = None
        results_callback = ResultCallback()
        try:
            tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                options=options,
                passwords=passwords,
                stdout_callback=results_callback,
            )
            rc = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
        return rc


def main():
    ansible = Ansible()
    rc = ansible.play()
    sys.exit(rc)

if __name__ == '__main__':
    main()
