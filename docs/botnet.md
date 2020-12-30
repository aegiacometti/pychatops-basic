# 1. Guia general
El software está en un repositorio privado de GitHub https://github.com/aegiacometti/netauto-dtv

En el directorio `home` del usuario `netdev`, están instalados los desarrollos bajo 
el directorio `/home/netdev/netauto`.

Los desarrollos son `pychatops` y `netconf-backup-gogs` (backup no activado).

La VM es un Oracle Linux en IBM Martinez con IP 172.22.162.11.
 
Es importante que esta IP se mantenga ya que la subnet tiene acceso a las VTY de los equipos de la region.
 
 
## 1.1. Pychatops
El objetivo de éste desarollo es contar con una integración de Python sobre Ansible
en el formato de **Bots**, de manera tal que podamos comunicarnos mediante Slack con
la infraestructura interna y asi lanzar playbooks de Ansible. 
Al finalizar su ejecucion el mensaje será reenviado a Slack.

La arquitectura es la siguiente:

![Arq-pychatops](https://github.com/aegiacometti/netauto-dtv/raw/master/docs/img/arq-pychatops.jpg)

Para más información sobre la arquitectura, casos de uso y extensiones revisar los siguientes links:

https://adriangiacometti.net/index.php/2020/02/21/keep-it-simple-with-automation-bots/

https://adriangiacometti.net/index.php/2020/01/19/chatops-a-new-way-of-delivering-1st-part-2/

https://adriangiacometti.net/index.php/2020/02/10/the-new-team-member-a-bot-chatops-part-3/


## 1.2. Netconf-backup
El objetivo basico es automatizar la toma de backup de los dispositivos de red y mantener un historico de dichas configuraciones.

Mediante el archivo de configuracion se puede habilitar las siguientes funcionalidades:

1.- Envio de mails cuando el backup termina y detalle si ha fallado en algun equipo

2.- Mismo objetivo que el punto anterior pero enviando mensajes a Slack

3.- Vincular el versionado del historico de configuraciones con Git, pudiendo utilizar GitHub cloud (privado y gratuito), o Gogs en el caso de requerir que los backups queden dentro de su infraesrtuctura. Ambas opciones son simplemente una GUI al sistema Git de linea de comando.

Para más información visitar los siguientes links:

https://adriangiacometti.net/index.php/2020/04/30/free-network-backup-with-gogs/

https://adriangiacometti.net/index.php/2020/04/13/free-cloud-network-backup-with-gui-and-messaging/


# 2. Instalación

Luego de instalado el sistema base de Oracle Linux, se requiere la instalacion acorde al siguiente link:

https://github.com/aegiacometti/netauto-dtv/docs/Install_Guide.md


# 3. Actualizaciones del software con Git y GitHub

El software se actualiza ejecutando en el directorio `/home/netdev/netauto` el comando `git pull origin master`.

Luego se reinician los servicios con:

`sudo service slack-bot-net restart`  (BotNet Slack IBM)

`sudo service slack-bot-net-dev restart`  (BotNet Slack desarrollo)

`sudo service slack-bot-skynet restart`  (BotNet Slack desarrollo)


# 4. Encripción de credenciales con Ansible Vault
Las claves estan encryptadas con Ansible Vault

Seguir la guia de configuracion del siguiente link:

https://adriangiacometti.net/index.php/2020/04/05/quick-start-ansible-vault/


# 5. Servicios

Los Bots son manejados por el process manager de Linux llamado `systemd`.

Para gestionar el estado de los Bots utilizar:

`sudo service slack-bot-net start/stop/status/restart`

`sudo service slack-bot-net-dev start/stop/status/restart`

`sudo service slack-bot-skynet start/stop/status/restart`


# 6. Capa de autorizacion local 

Ademas de la autorizacion remota en Slack, agregamos una 2da capa de autorizacion pero local. Esta capa tendra 2 archivos donde deberan ingresarse los ID por
grupo y los comandos por grupo. Estas operaciones se realizan mediante el chatBot `@BotNet users`

Ademas se puede limitar a que el Bot solo escuche un canal determinado, pero esto no tiene suficiente razon de ser.


# 7. Commandos y ayudas

Para ver los comandos disponibles escribir en slack `@BotNet help`.

Para ver el help de cada uno de los comandos utilizar `@BotNet help nombredelcomando`


# 8. Estructura de directorios
Siguiendo la siguiente estructura el software se encuentra instalado en el home del usuario `netdev` en el subdirectorio `~/netauto`.

| Directorio / Archivo              | Descripción                               |
|-----------------------------------|-------------------------------------------|
|~/.ansible.cfg                     | Archivo de configuracion de Ansible       |
|-----------------------------------|-------------------------------------------|
|~/netauto                     | Directorio raiz general                   |
|~/netauto/pychatops.config | Archivo de configuración general          |
|-----------------------------------|-------------------------------------------|
|~/netauto/devices             | Inventario general de Ansible      |      
|~/netauto/devices/hosts       | Dispositivos    |
|~/netauto/devices/group_vars  | Credenciales |
|~/netauto/devices/group_vars/all.yml  | Variables que aplican a todo el inventario |
|~/netauto/devices/group_vars/xxx  | Variables que aplican a grupos definidos en `hosts` |
|-----------------------------------|-------------------------------------------|
|~/netauto/docs  | Documentacion e imagenes |
|-----------------------------------|-------------------------------------------|
|~/netauto/netconf-backup  | Directorio raiz de netconf-backup |
|~/netauto/netconf-backup/netconf-backup.yml  | Playbook princial y configuracion de netconf-backup |
|~/netauto/netconf-backup/backups  | Backup completo de configuraciones de equipos |
|~/netauto/netconf-backup/backups/gogs-staging  | Staging de backup de configuraciones |
|~/netauto/netconf-backup/playbooks  | Playbooks de Ansible para **netconf-backup** |
|~/netauto/netconf-backup/scripts  | Scripts Python para el procesado de información retornada de los playbooks |
|-----------------------------------|-------------------------------------------|
|~/netauto/pychatops | Directorio raiz de pychatops |
|~/netauto/pychatops/ansible | Directorio del modulo de Ansible para **pychatops** |
|~/netauto/pychatops/ansible/playbooks | Playbooks para **pychatops** |
|~/netauto/pychatops/ansible/playbooks/network | Playbooks de network |
|~/netauto/pychatops/ansible/playbooks/network/scripts | Scrips Python para el procesado de información retornada de los playbooks y envio de mensajes a Slack|
|~/netauto/pychatops/logs | **Logs de comandos y debug de los bots** |
|~/netauto/pychatops/slack/slack-bot-net.py | Script **Bot Networking Slack IBM** |
|~/netauto/pychatops/slack/slack-bot-net-dev.py | Script **Bot Skynet Slack Dev** |
|~/netauto/pychatops/slack/slack-bot-skynet.py | Script **Bot Skynet Slack Dev** |
|~/netauto/pychatops/slack/authorizations | Directorio para archivos de autorizaciones locales |
|~/netauto/pychatops/slack/authorizations/auth-user-net.json | Bot Networking command authorization file |
|~/netauto/pychatops/slack/bots/net | Commandos Bot Networking |
|~/netauto/pychatops/slack/bots/net/data | Directorio para informacion extra que puede utilizar Bot Networking |
|~/netauto/pychatops/slack/bots/net/data/links.txt | Archivo inventario de links |
|~/netauto/pychatops/slack/bots/net/disabled_cmds | Directorio para mover comandos y deshabilitarlos automaticamente |
|~/netauto/pychatops/slack/bots/net-dev/data | Directorio para informacion extra que puede utilizar Bot Networking |
|~/netauto/pychatops/slack/bots/net-dev/data/links.txt | Archivo inventario de links |
|~/netauto/pychatops/slack/bots/net-dev/disabled_cmds | Directorio para mover comandos y deshabilitarlos automaticamente |
|~/netauto/pychatops/slack/bots/skynet | Commandos Bot Skynet |
|~/netauto/pychatops/slack/bots/skynet/data | Directorio para informacion extra que puede utilizar Bot Networking |
|~/netauto/pychatops/slack/bots/skynet/disabled_cmds | Directorio para mover comandos y deshabilitarlos automaticamente |
|~/netauto/pychatops/slack/common | Scripts Python comunes a todos los Bots |
|~/netauto/pychatops/slack/services | Archivos de referencia de configuration inicial |
|~/netauto/pychatops/slack/tests/integration/tests-OK/slack-send-test.py | Script Python para ejecucion de tests |
|~/netauto/pychatops/slack/tests/integration/tests-OK/tests-Net.txt | Lista de tests a ejecutar en formato chat |
|~/netauto/pychatops/slack/tests/integration/tests-OK/tests-skynet.txt | Lista de tests a ejecutar en formato chat  |

# 9. Device Support Matrix


### Network devices

| Command       | IOS-SSH | IOS-Telnet | Nexus | ASA | FMC | F5 | Fortinet | ACI | OCI | 
|---------------|:-------:|:----------:|:-----:|:---:|:---:|:---:|:---:|:---:|:---:|
| block_ip | | | | x | x | | | | |
| unblock_ip | | | | x | x | | | | |
| cbr | x | x | x | x | | | | | |
| device.status | x | | | | | | | | |
| ping | x | | x | | | | | | |
| mping | x | | x | | | | | | |
| trace | x | | x | | | | | | |
| mtrace | x | | x | | | | | | |
| show | x | x | x | x | | | | | |
| mshow | x | x | x | x | | | | | |
| check.vpn | | | | x | | | | | |
| check.vpn.filter | | | | x | | | | | |
| list.vpn | | | | x | | | | | |
| reset.vpn | | | | x | | | | | |
| status.vpn | | | | x | | | | | |
| users | na | na | na | na | na | na | na | na | na |
| help | na | na | na | na | na | na | na | na | na |
| show.inventory | na | na | na | na | na | na | na | na | na |
| *conf | x | | | | | | | | |
| *mconf | x | | | | | | | | |
| *backup | x | x | x | x |  | x | | | | |
| *link.status | x | | | | | | | | |
| **asa.pkt.trace | | | | x | | | | | |
| **lb.node | | | | | | x | | | |
| **lb.pool | | | | | | x | | | |
| **lb.vs | | | | |  |x | | | |

*finished but not deployed*
**not finished*

###Extras 

| command | desc |
|---|---|
| help | show available commands |
| help command | show help of a specific command |
| show.inventory xxx | show inventory, with filter support |
| link.list | show link inventory |



# 10. Tips

- Podes ver si el Bot está conectado a Slack, con el indicador de presencia en verde dentro de Slack.

- Utilicen los help de los comando que soportan los bots, y el help de cada uno de los comando para ver que son, que hace, como se escribe la sintaxis.

- A la ejecucion manual de todos los playbooks de Ansible, le podes agregar modo verbose con `-vvvv`, y ademas si le pones `-l hostx o host*` le estas diciendo limitate a este host más alla de que estas matcheando varios equipos mas.

- En el archivo `netauto/devices/hosts` podes armar grupos de equipos, poniendo el nombre del grupo entre corchetes `[xxx]` y a continuacion los equipos de ese grupo.

- Ademas podes anidarlos como para armar sitios y equipos por sitio

```
[switches]
pepe

[router]
jose

[sitio:children]
switches
router
```

- En el directorio `~/netauto/devices/group_vars` se arman los archivos para poner las credenciales de los equipos 1
sola vez. Los nombres de los archivo en ese directorio deben ser los mismos que los nombres de los grupos que se
armaron en el archivo **hosts** del punto anterior.
