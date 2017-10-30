#!/usr/bin/python
# -*- coding: utf-8 -*-

# 2016 - Gaetan trellu (goldyfruit) - <gaetan.trellu@incloudus.com>
# 2016 - Veros Kaplan (verosk)

# pcs_command_exists checks if command exists
# Example: pcs_command_exists('/usr/sbin/pcs')
def pcs_command_exists(cmd):
    try:
        os.stat(cmd)
        return True
    except:
        return False

# pcs_svc_running checks if a process is running
# Example: pcs_svc_running('[p]acemakerd')
def pcs_svc_running(svc):
    try:
        ps = subprocess.Popen(['ps', 'faux'], stdout=subprocess.PIPE)
        grep = subprocess.Popen(['grep', svc, '-c'],
                            stdin=ps.stdout,
                            stdout=subprocess.PIPE)
        ps.stdout.close()
        output = grep.communicate()[0]
        ps.wait()

        if output == '1\n':
            return True
    except:
        return False

def main():
    module = AnsibleModule(
        argument_spec = dict(
            command   = dict(required=True, choices=['auth', 'start', 'sync', 'destroy', 'stop', 'standby', 'unstandby']),
            hosts     = dict(required=False),
            node      = dict(required=False),
            force     = dict(default='no', required=False, choices=['yes', 'no']),
            username  = dict(required=False),
            all_nodes = dict(default='no', required=False, choices=['yes', 'no']),
            password  = dict(required=False),
        ),
        supports_check_mode=True,
    )

    # Check if pcs command exists.
    if pcs_command_exists('/usr/sbin/pcs') is not True:
        module.fail_json(msg="Unable to find the 'pcs' command...")

    # Check if Pacemaker is running.
    if pcs_svc_running('[p]acemakerd') is not True and module.params['command'] != 'stop' and module.params['command'] != 'destroy':
        module.fail_json(msg="pacemakerd is not running...")

    # Check if Corosync is running.
    if pcs_svc_running('[c]orosync') is not True and module.params['command'] != 'stop' and module.params['command'] != 'destroy':
        module.fail_json(msg="corosync is not running...")

#    # Check if pcsd is running.
#    if pcs_svc_running('[p]csd start') is not True:
#        module.fail_json(msg="pcsd is not running...")

    cmd = "pcs status xml" % module.params
    rc, out, err = module.run_command(cmd)
    exists = (rc is 0)

    if module.params['command'] not in ['standby', 'unstandby']:
        # check cluster exists
        if exists and module.params['force'] == 'no':
            module.exit_json(changed=False, msg="Pacemaker cluster already exists.")
        elif exists and module.params['force'] == 'yes':
            changed=True
        elif module.check_mode:
            changed=True

    if module.params['command'] == 'auth':
        if not module.params.has_key('hosts'):
            module.fail_json(msg="Missing required arguments: hosts")
        if module.params.has_key('force'):
            cmd = 'pcs cluster %(command)s %(hosts)s -u %(username)s -p %(password)s --force'
            changed=True
        else:
            cmd = 'pcs cluster %(command)s %(hosts)s -u %(username)s -p %(password)s'
            changed=True

    if module.params['command'] == 'start':
        if module.params['all_nodes'] == 'yes':
            cmd = 'pcs cluster %(command)s --all'
            changed=True
        else:
            cmd = 'pcs cluster %(command)s'
            changed=True

    if module.params['command'] == 'sync':
        cmd = 'pcs cluster %(command)s'
        changed=True

    if module.params['command'] == 'destroy':
        cmd = 'pcs cluster %(command)s --all'
        changed=True

    if module.params['command'] == 'stop':
        cmd = 'pcs cluster %(command)s --all'
        changed=True


    if module.params['command'] in ['standby', 'unstandby']:
        command= module.params['command']
        if 'node' not in module.params:
            module.fail_json(msg="Missing required argument: node")
        #
        import xml.etree.ElementTree as ET
        root = ET.fromstring(out)
        target_node = root.find(".//node[@name='%(node)s']" % module.params)
        if target_node is None:
            module.fail_json(msg="Unable to find node '%(node)s'" % module.params)
        try:
            is_standby = target_node.attrib['standby']
        except KeyError:
            module.fail_json(
                msg="Unable to find atrrib 'standby' on node %(node)s" % module.params)
        assert is_standby.lower() in ['true','false']
        #
        if is_standby.lower() == 'true' and command == 'standby':
            module.exit_json(changed=False)
        if is_standby.lower() == 'false' and command == 'unstandby':
                module.exit_json(changed=False)
        #
        cmd = 'pcs cluster %(command)s %(node)s'
        changed=True

    # Run command.
    cmd = cmd % module.params
    rc, out, err = module.run_command(cmd)
    if rc is 1:
        module.fail_json(msg="Execution failed.\nCommand: `%s`\nError: %s" % (cmd, err))

    module.exit_json(changed=changed)

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
