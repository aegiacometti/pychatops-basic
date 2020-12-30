Basically, what I’m doing here, is using Slack as a messaging interface between the Internet and your internal network, and Python as the mediator for getting those messages, take action and post back to Slack the results.

The “take action” part it’s also an interface to launch whatever OS command, in this case, interfacing with Ansible, Salt and other Python scripts (since they are multi-platform they support almost every OS, network, servers, etc).

The following diagram shows the interaction flow and directions:

![Arq-pychatops](https://github.com/aegiacometti/pychatops-basic/raw/master/docs/img/arq-pychatops.jpg)

The Automation Bots are daemonized Python scripts and managed by systemd. Which means easy control of the process.

If someone mentions the Bot name in Slack, then the Bot will parse that message, check user rights, permissions, validate the requested action and add it to a simple scheduler.

The Bot by using Ansible, Salt or a Python script, will ask the remote device to execute the action. The connectivity between the Bot and the remote device is achieved by using the standard methods provided by each device type. Let’s say: Windows – PowerShell, Networking and Linux – SSH and APIs.

Finally, the requested action at the remote device is also part of the standard ones they already have. Some examples: ping, traceroute, show run, conf t, dir, get-service, set-service, sudo service and so on per each device type.

The Bot script is a generic multi-function Bot. When systemd launch a Bot, it will load the specific parameters and available modules. That’s it.

![Arq-pychatops-2](https://github.com/aegiacometti/pychatops-basic/raw/master/docs/img/arq-pychatops-2.png)

The Automation Bots have a simple plugin architecture. So, adding new functionalities doesn’t require to modify the base code, just add the plugin to the Bot folder. The plugin is just one file and is also very simple.

![Arq-pychatops-3](https://github.com/aegiacometti/pychatops-basic/raw/master/docs/img/arq-pychatops-3.png)

Just for curiosity, check this link how interesting is to add nice graphs with ELK to see how the bot are working and the code is behaving.

https://adriangiacometti.net/index.php/2020/04/05/free_analytics_with_elk/

![Arq-pychatops-4](https://github.com/aegiacometti/pychatops-basic/raw/master/docs/img/ELK-dashboard-automation_bots.png)
