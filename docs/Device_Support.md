
###Network

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

