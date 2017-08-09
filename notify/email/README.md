## notify email

this is the directory, with the email notifier module and the config file.<br>
add a config.ini with a section for each project name and it's mail recipients.
the config is ignored so no information is leaked to repo.<br>
it's content should look like this:<br>

```
[project_name1]<br>
server = your companys mail server<br>
sender = email address of sender<br>
receiver = email address of receiver1, email address of receiver2 ...
 
[project_name2]<br>
server = your companys mail server<br>
sender = email address of sender<br>
receiver = email address of receiver1, email address of receiver3 ...
```
