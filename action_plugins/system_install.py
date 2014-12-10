# -*- coding: utf-8 -*-

# Copyright © 2014 Sébastien Gross <seb•ɑƬ•chezwam•ɖɵʈ•org>
# Created: 2014-03-11
# Last changed: 2014-10-24 19:00:27
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.
#
# This file is not part of Ansible

import os

import ansible.utils.template as template
from ansible.runner.return_data import ReturnData
from ansible import utils

import glob
import subprocess
import pipes


## fixes https://github.com/ansible/ansible/issues/3518
# http://mypy.pythonblogs.com/12_mypy/archive/1253_workaround_for_python_bug_ascii_codec_cant_encode_character_uxa0_in_position_111_ordinal_not_in_range128.html
import sys
reload(sys)
sys.setdefaultencoding("utf8")

class ActionModule(object):

    def __init__(self, runner):
        self.runner = runner
        #self.hard_drives = []

    def _copy_setup_storage(self):
        """Copy C(setup-storage) and its default configuration to taget system."""
        for d in [ 'setup-storage', 'setup-storage/conf.d' ]:
            self.runner._low_level_exec_command(
                self.conn, 'mkdir -p %s/%s' % (self.tmp_path, d),
                None, sudoable=False)
            for file in glob.glob('%s/*' % d):
                if os.path.isfile(file):
                    self.conn.put_file(file, self.tmp_path + file)

    def run(self, conn, tmp_path, module_name, module_args, inject,
            complex_args=None, **kwargs):
        ''' handler for file transfer operations '''

        # load up options
        options  = {}
        if complex_args:
            options.update(complex_args)
        options.update(utils.parse_kv(module_args))

        if "-tmp-" not in tmp_path:
            tmp_path = self.runner._make_tmp_path(conn)

        self.tmp_path = tmp_path
        self.conn = conn
        self.facts = inject

        self._copy_setup_storage()

        # copy user defined partion file if needed
        partition = options.get('partition')
        if not partition is None and partition != 'auto':
            fnd = utils.path_dwim(
                os.path.sep.join((self.runner.basedir, 'files')),
                partition)
            if not os.path.exists(fnd):
                fnd = utils.path_dwim_relative(
                    partition, 'files', partition, self.runner.basedir)
            self.conn.put_file(
                fnd,
                os.path.sep.join([self.tmp_path, 'setup-storage', 'conf.d', partition]))

        ret=self.runner._execute_module(
            conn, tmp_path, 'system_install',
            module_args, inject=inject,
            complex_args=complex_args)

        return ret
