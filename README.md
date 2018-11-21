# AnsibleFest2017
Managing Shared Secrets demo code, from Ansible Fest London 2017

From my AnsibleFest Tech Deep Dive Session.   Vagrant and Ansible code to demo automatically generated passwords, using Postgres replication as an example.   Built for Centos/RHEL.

Demo screencast: https://vimeo.com/224764672

### Create Vagrant Instances
Create Vagrant instances to run the vault, see the sub-dir _vagrant_ from this repo.

### Ansible Bootstrap
Bootstrap the new vault instance, installing the ssh key (should match private_key_file from ansible.cfg).   We also install the hosts file, picked up from /vagrant/etc_hosts on the new vault instance.   When not using Vagrant you'll need to workaround this and populate the /etc/hosts file.
```
ansible $ $ ansible-playbook -k -K bootstrap_hosts.yml 
SSH password: 
SUDO password[defaults to SSH password]: 

PLAY [all] *******************************************************************************************************************************************

TASK [install Ansible ssh key] ***********************************************************************************************************************
ok: [vault]
ok: [api2]
ok: [api1]
ok: [proxy]
ok: [database]

TASK [copy /etc/hosts to remote] *********************************************************************************************************************
ok: [database]
ok: [proxy]
ok: [api2]
ok: [api1]
ok: [vault]

TASK [install net-tools] *****************************************************************************************************************************
changed: [api1]
changed: [database]
changed: [proxy]
changed: [api2]
changed: [vault]

PLAY RECAP *******************************************************************************************************************************************
api1                       : ok=3    changed=1    unreachable=0    failed=0   
api2                       : ok=3    changed=1    unreachable=0    failed=0   
database                   : ok=3    changed=1    unreachable=0    failed=0   
proxy                      : ok=3    changed=1    unreachable=0    failed=0   
vault                      : ok=3    changed=1    unreachable=0    failed=0 
```

### Setup Demo
Now you can go ahead and configure the instances
```
ansible $ ansible-playbook site.yml
```

### Quick Status Check
The master node (node1) should show both slaves nodes connected and streaming replication data:
```
ansible $ ssh root@node1
root@node1's password: 

[root@node1 ~]# su - postgres
-bash-4.2$ psql
psql (9.2.18)
Type "help" for help.

postgres=# select r.client_addr, r.usename, r.state, r.sent_location, s.passwd from pg_stat_replication as r inner join pg_shadow as s on r.usename = s.usename;
  client_addr  |  usename   |   state   | sent_location |               passwd                
---------------+------------+-----------+---------------+-------------------------------------
 172.28.128.17 | repl_node3 | streaming | 0/5000D88     | md58b233a7e5a5472f6023fdbd31fb0e73c
 172.28.128.16 | repl_node2 | streaming | 0/5000D88     | md58174d1b63a85c305751b1ffd7824e0a5
(2 rows)
```
Now we can rotate the slave node credentials:
```
ansible $ ansible-playbook rotate.yml 

PLAY [slaves] *********************************************************************************************************************************

TASK [explicit charset for greater control] ***************************************************************************************************
ok: [node2]
ok: [node3]

TASK [generate a random string, length and charset may be application specific] ***************************************************************
ok: [node2]
ok: [node3]

TASK [stop postgres on the slave] *************************************************************************************************************
changed: [node2]
changed: [node3]

TASK [ensure replication user on the master has correct credentials] **************************************************************************
changed: [node2 -> node1]
changed: [node3 -> node1]

TASK [update slave recovery.conf with new connection info] ************************************************************************************
changed: [node2]
changed: [node3]

TASK [start postgres on the slave] ************************************************************************************************************
changed: [node2]
changed: [node3]

PLAY RECAP ************************************************************************************************************************************
node2                      : ok=6    changed=4    unreachable=0    failed=0   
node3                      : ok=6    changed=4    unreachable=0    failed=0
```
On the slaves the connection string data:
```
ansible $ ssh root@node2
root@node2's password: 
Last login: Tue Dec  6 13:39:33 2016
[root@node2 ~]# cat /var/lib/pgsql/data/recovery.conf 
standby_mode = 'on'
primary_conninfo = 'host=node1 port=5432 user=repl_node2 password=ratCcFRm27XE3BKazBbw'
trigger_file = '/tmp/trigger'
```