import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import offensive_modules.mythic_control as mc
import offensive_modules.sliver_control as sc
import offensive_modules.empire_control as ec
import offensive_modules.covenant_control as cc


def test_mythic_cmd_build():
    cmd = mc.build_mythic_cmd('install')
    script = os.path.join(os.path.dirname(mc.__file__), '..', 'github_scanners', 'mythic', 'run.sh')
    assert cmd[:2] == ['bash', script]
    assert cmd[2] == 'install'


def test_sliver_cmd_build():
    cmd = sc.build_sliver_cmd('install')
    script = os.path.join(os.path.dirname(sc.__file__), '..', 'github_scanners', 'sliver', 'run.sh')
    assert cmd[:2] == ['bash', script]
    assert cmd[2] == 'install'


def test_empire_cmd_build():
    cmd = ec.build_empire_cmd('install')
    script = os.path.join(os.path.dirname(ec.__file__), '..', 'github_scanners', 'empire', 'run.sh')
    assert cmd[:2] == ['bash', script]
    assert cmd[2] == 'install'


def test_covenant_cmd_build():
    cmd = cc.build_covenant_cmd('install')
    script = os.path.join(os.path.dirname(cc.__file__), '..', 'github_scanners', 'covenant', 'run.sh')
    assert cmd[:2] == ['bash', script]
    assert cmd[2] == 'install'

