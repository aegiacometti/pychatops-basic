# 1. Instalación

Example under Linux Ubuntu based distro:

`sudo apt-add-repository ppa:ansible/ansible`

`sudo apt-get update`

`sudo apt-get install python3-pip`

`sudo pip3 install setuptools --upgrade`

`python3 setup.py sdist bdist_wheel`

`sudo apt-get install git`

`sudo pip3 install ansible`

`sudo pip3 install slackclient==1.3.2`

`sudo pip3 install dnspython`

`sudo pip3 install paramiko`

`sudo pip3 install psutil`

`sudo pip3 install ansible-vault`

`sudo pip3 install scp`

If applicable to your deploy

`sudo pip3 install f5-sdk`

`sudo pip3 install fmcapi`

`sudo pip3 install pyFG`

`sudo apt-get install sshpass`

`sudo pip3 install "pywinrm>=0.3.0"`

`sudo pip3 install fortiosapi`

`sudo pip3 install oci`

`ansible-galaxy collection install fortinet.fortios:1.0.14`

From the install user directory:

`git clone https://github.com/aegiacometti/pychatops.git`

`git clone https://github.com/aegiacometti/netconf-cloud-backup.git`

`ansible-galaxy install ansible-network.network-engine`

`wget https://raw.githubusercontent.com/ansible/ansible/devel/examples/ansible.cfg -O $HOME/.ansible.cfg`


# 2. Configuración

### cliente SSH
Read and follow this link

https://github.com/aegiacometti/netconf-backup#special-ssh-connectivity-notes

### $HOME/.ansible.cfg
```
ansible_python_interpreter=/usr/bin/python3
inventory = /home/adrian/netor-master/netor/ansible/hosts
forks		= 100
poll_interval   = 5
transport = paramiko
host_key_checking = False
vault_password_file = ./.vault_pass
host_key_auto_add = True
pipelining = True
connect_timeout = 20
network_cli_retries = 2
command_timeout = 60
```

### $HOME/.profile

Add

`export ANSIBLE_VAULT_PASSWORD_FILE="$HOME/.vault_pass"`

Run

`chmod 600 ~/.vault_pass`

### /etc/environment

Add

```
PYTHONPATH=/home/netauto/netorchestra/
```

### Servicios en systemd

Agregar servicios

`sudo cp pychatops/netor/slack/services/slack-bot-net.service /lib/systemd/system`

`sudo cp pychatops/netor/slack/services/slack-bot-skynet.service /lib/systemd/system`

Enable and disable services
`sudo systemctl enable xxx.service`
`sudo systemctl disable xxx.service`

Start services
`sudo systemctl start xxx.service`
`sudo systemctl stop xxx.service`

Allow exec to owner userID, and change the userID in the file `slack-bots` accordingly to your deploy
`sudo cp pychatops/netor/slack/services/slack-bots /etc/sudoers.d/`

### crontab
sudo contrab -e
*/30 * * * * /etc/cron.daily/logrotate 

### logrotate

Copy or "ln -s" the commando `logrotate` to subdirectory `cron.daily`.

Add to `logrotate.conf` the following structure per each bot/service.

```
/home/netdev/netauto/pychatops/log/slack-bot-net.log {
    compress
    dateext
    weekly
    rotate 5
    maxsize 100M
    copytruncate
}
```

```
/home/netdev/netauto/pychatops/log/slack-bot-skynet.log {
    compress
    dateext
    weekly
    rotate 5
    maxsize 100M
    copytruncate
}
