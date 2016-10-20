# -*- coding: utf-8 -*-

# Copyright © 2014 Sébastien Gross <seb•ɑƬ•chezwam•ɖɵʈ•org>
# Created: 2014-03-11
# Last changed: 2016-10-20 17:04:02
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.
#
# This file is not part of Ansible

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from ansible import constants as C
from ansible.plugins.action import ActionBase
from ansible.utils.boolean import boolean
from ansible.utils.hashing import checksum
from ansible.utils.unicode import to_bytes

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

import glob
import subprocess
import pipes

def display(msg):
    from ansible.utils.display import Display
    Display().display(msg, color='yellow')
    

class ActionModule(ActionBase):

    def _copy_setup_storage(self, tmp):
        """Copy C(setup-storage) and its default configuration to taget system."""
        for d in [ 'setup-storage', 'setup-storage/conf.d' ]:
            for src in glob.glob('%s/*' % d):
                if os.path.isfile(src):
                    tmp_src = self._connection._shell.join_path(
                        tmp, src)
                    display('Copy %s -> %s' % (src, tmp_src))
                    self._transfer_file(src, tmp_src)

    def run(self, tmp=None, task_vars=None):
        ''' handler for file transfer operations '''
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        remote_user = task_vars.get('ansible_ssh_user') or self._play_context.remote_user
        partition = self._task.args.get('partition', None)
        
        display("in run()")

        if tmp is None or "-tmp-" not in tmp:
            tmp = self._make_tmp_path(remote_user)
            self._cleanup_remote_tmp = False
        self._low_level_execute_command('mkdir -p %s/setup-storage/conf.d' % tmp,sudoable=True)
        # display("tmp = '%s'" % tmp)

        
        self._copy_setup_storage(tmp)
        if not partition is None and partition != 'auto':
            
            for d in [ 'files', 'setup-storage/conf.d' ]:
               _file = self._loader.path_dwim_relative(
                   '.', d, partition)
               if os.path.exists(_file):
                   _dest = self._connection._shell.join_path(
                       tmp, 'setup-storage', 'conf.d', os.path.basename(partition))
                   display('%s -> %s' % (_file, _dest ))
                   self._transfer_file(_file, _dest)

        new_module_args = self._task.args.copy()
        new_module_args.update(dict(
            __ansible_tmp = tmp
            ))
        result.update(
            self._execute_module('system_install',
                                 module_args=new_module_args,
                                 task_vars=task_vars,
                                 tmp=tmp))

        return result
