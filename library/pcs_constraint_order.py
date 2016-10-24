#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: pcs_constraint_order
'''

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
        argument_spec  = dict(
            options    = dict(required=False, type='dict'),
            first      = dict(require=True),
            first_action = dict(default='start'),
            second     = dict(require=False),
            second_action=dict(default='start'),
        ),
        supports_check_mode=True,
    )


    # Check if pcs command exists.
    if pcs_command_exists('/usr/sbin/pcs') is not True:
        module.fail_json(msg="Unable to find the 'pcs' command...")

    # Check if Pacemaker is running.
    if pcs_svc_running('[p]acemakerd') is not True:
        module.fail_json(msg="pacemakerd is not running...")

    # Check if Corosync is running.
    if pcs_svc_running('[c]orosync') is not True: 
        module.fail_json(msg="corosync is not running...")

    # Get ordering constraints
    rc,out,err = module.run_command('pcs constraint order show')
    if rc != 0:
        module.fail_json(msg="Unable to run command", cmd="pcs constraint order show")

    if 'first' not in module.params:
        module.fail_json(msg="Invocation failed. Parameter 'first' should be resource id")
    if 'second' not in module.params:
        module.fail_json(msg="Invocation failed. Parameter 'second' should be resource id")
    looking_for = '%(first_action)s %(first)s then %(second_action)s %(second)s ' % module.params

    parts = out.split('\n')
    for ln in parts:
        if ln.find(looking_for) != -1:
            module.exit_json(changed=False, msg="Constraint exists", line=ln.strip())
    #
    if module.params['options']:
        options = module.params['options'].items()
        options = ' '.join(['%s="%s"' % (key, value) for (key, value) in options])
        module.params['options'] = options
    else:
        module.params['options'] = ''
    #
    cmd = 'pcs constraint order %(first_action)s %(first)s then %(second_action)s %(second)s %(options)s' \
                    % module.params

    if module.check_mode:
        module.exit_json(changed=changed, msg="Created constraint", cmd=cmd)

    # Run command.
    cmd = cmd % module.params
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Execution failed.\nError: %s" % err,
                         cmd=cmd)
    else:
        module.exit_json(changed=True,
                         msg="Created constraint",
                         cmd=cmd)

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
