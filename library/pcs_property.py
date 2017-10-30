#!/usr/bin/python
# -*- coding: utf-8 -*-

# 2016 - Gaetan trellu (goldyfruit) - <gaetan.trellu@incloudus.com>
# 2014 - Jonathan Araña Cruz (jonhattan) - <onhattan@faita.net>
# 2016 - Veros Kaplan (verosk) verosk@users.github.com

DOCUMENTATION = '''
---
module: pcs_property
short_description: Manages Pacemaker cluster properties with pcs property command.
description:
 - This module configures Pacemaker cluster properties.
options:
  state:
    required: false
    default: present
    choices: [ "absent", "present" ]
    description:
    - Whether the property should be present or absent
  node:
    required: false
    default: no
    choices: [ "yes", "no" ]
    description:
      - Add the --node argument to the pcs property set/unset command
  force:
    required: false
    default: no
    choices: [ "yes", "no" ]
    description:
      - Add the --force argument to the pcs property set/unset command
  nodename:
    required: false
    description:
      - Name of the node where the attribute should be applied
  name:
    required: true
    description:
      - Name of the property/attribute
  value:
    required: true
    description:
      - Value of the property/attribute
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
        argument_spec = dict(
            state     = dict(default='present', choices=['present', 'absent']),
            node      = dict(default='no', choices=['yes', 'no'], required=False),
            force     = dict(default='no', choices=['yes', 'no'], required=False),
            nodename  = dict(required=False),
            name      = dict(required=True),
            value     = dict(required=True),
        ),
        supports_check_mode=True,
    )

    # Check if pcs command exists.
    pcs_command_exists('/usr/sbin/pcs')
    if pcs_command_exists('/usr/sbin/pcs') is not True:
        module.fail_json(msg="Unable to find the pcs command...")

    # Check if Pacemaker is running.
    if pcs_svc_running('[p]acemakerd') is not True:
        module.fail_json(msg="pacemakerd is not running..")

    # Check if Corosync is running.
    if pcs_svc_running('[c]orosync') is not True:
        module.fail_json(msg="corosync is not running...")

#    # Check if pcsd is running.
#    if pcs_svc_running('[p]csd start') is not True:
#        module.fail_json(msg="pcsd is not running...")

    # Get current property value.
    if module.params['node'] == 'yes' and module.params['nodename']:
        cmd = "pcs property list | grep %(nodename)s | awk '{ for(i=1; i<=NF; i++) { if($i == \"%(name)s=%(value)s\") { print $i } } }'" % module.params
        node = True
    else:
        cmd = "pcs property show %(name)s | sed -n '/Node Attributes:/q;p' | awk '/^ / { print $2 }'" % module.params
        node = False
    rc, out, err = module.run_command(cmd, use_unsafe_shell=True)
    value = out.strip()

    if module.params['state'] == 'absent':
        if value != '':
            changed = True
            if not module.check_mode:
                if module.params['node'] == 'yes' and module.params['nodename']:
                    cmd = 'pcs property unset --node %(nodename)s %(name)s' % module.params
                elif module.params['node'] == 'yes' and module.params['nodename'] and module.params['force'] == 'yes':
                    cmd = 'pcs property unset --node %(nodename)s %(name)s --force' % module.params
                elif module.params['force'] == 'yes':
                    cmd = 'pcs property unset %(name)s --force' % module.params
                else:
                    cmd = 'pcs property unset %(name)s' % module.params
                module.run_command(cmd)
        else:
            changed = False
        module.exit_json(changed=changed)
    else:
        if node:
            property = ('%(name)s=%(value)s') % module.params
        else:
            property = module.params['value']
        if value != property:
            changed = True
            if not module.check_mode:
                if module.params['node'] == 'yes' and module.params['nodename']:
                    cmd = 'pcs property set --node %(nodename)s %(name)s=%(value)s' % module.params
                elif module.params['node'] == 'yes' and  module.params['node'] and module.params['force'] == 'yes':
                    cmd = 'pcs property set --node %(nodename)s %(name)s=%(value)s --force' % module.params
                elif module.params['force'] == 'yes':
                    cmd = 'pcs property set %(name)s=%(value)s --force' % module.params
                else:
                    cmd = 'pcs property set %(name)s=%(value)s' % module.params
                module.run_command(cmd)
        else:
            changed = False
        module.exit_json(changed=changed, prev="|%s|" % value, msg="%(name)s=%(value)s" % module.params)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
