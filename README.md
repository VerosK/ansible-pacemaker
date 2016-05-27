pacemaker
=========

Ansible role to configure Pacemaker and pacemaker resources.
 
Based on https://github.com/sbitio/ansible-pacemaker work, which was originally
developed on CentOS 6 with Pacemaker version 1.1.10. Current version updated
and tested Ubuntu xenial. More distributions are going to be tested.

This role provides several [modules](library) to manage Pacemaker configuration
with `pcs` tool. 

`pcs` is not available on Debian Wheezy, where `crm` is the tool available. In a
future we may add support for it.

You will likely want to use Pacemaker in conjunction with Corosync. Checkout
[sbitmedia.corosync](https://galaxy.ansible.com/list#/roles/690), and make sure
this role is included later. See example below.

Role Variables
--------------

See defaults in [`defaults/main.yml`](defaults/main.yml) for reference.

TODO: Add example playbook here.

License
-------

BSD

Author Information
------------------

Original author: Jonathan Araña Cruz - SB IT Media, S.L.

Another original author: ..*[]:
 
Last author: [Veros Kaplan](https://github.com/verosk/)


