## notify slack

this is the directory, with the slack notifier module and the config file.<br>
add a config.ini with a section for each project name and it's mail recipients.
the config is ignored so no information is leaked to repo.<br>
it's content should look like this:<br>

[project_name1]<br>
token = your company's slack token<br>
channel = slack channel<br>

[project_name2]<br>
token = your company's slack token<br>
channel = slack channel<br>
