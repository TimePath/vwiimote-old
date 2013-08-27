#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import subprocess


class Main:
    """"""

    def __init__(self):
        """killall screen to kill everything"""
        scripts = [
            "server.py",
            "WMD.py",
            #"ui.py",
            ]

        terminal = ['xfce4-terminal']
        screen = ""#"screen -q"
        for idx, script in enumerate(scripts):
            if idx == 0:
                terminal.extend(['--window'])  # --window
            else:
                terminal.extend(['--tab'])
            terminal.extend(['-T', script])
            terminal.extend(['-e', '''
                %(screen)s bash -c '
                python %(script)s
                echo
                echo Finished execution
                read
                '
            ''' % locals()])
        subprocess.call(terminal)

if __name__ == '__main__':
    Main()
    sys.exit()