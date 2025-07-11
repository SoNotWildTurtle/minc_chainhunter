import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import offensive_modules.mythic_control as mc


def test_mythic_cmd_build():
    cmd = mc.build_mythic_cmd('install')
    script = os.path.join(os.path.dirname(mc.__file__), '..', 'github_scanners', 'mythic', 'run.sh')
    assert cmd[:2] == ['bash', script]
    assert cmd[2] == 'install'

