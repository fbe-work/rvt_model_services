## notify requests post

this is the directory, with the req_post notifier module and the config file.<br>
add a config.ini with a section for each project name and it's message recipients.
the config is ignored so no information is leaked to repo.<br>
it's content should look like this:<br>

```
[project_name1]
url = server url to post to
ssl_verify = true
```
