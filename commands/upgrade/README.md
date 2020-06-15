# command: upgrade

## command description
`upgrade` will search through the directory, in which the rvt model is located, 
that got specified when running the command and process each workshared or 
standalone rvt model in there.

If the file found is: 

* a rvt model,
* that is not blacklisted in `skip_models`, 
* not already existing as an upgraded model
* not an `*.0001.rvt` rvt backup file, 

rvt_model_services will open the models upgrade (where needed) to the 
rvt version specified at rvt_model_services command start e.g. `--rvt_ver=2019` 
and save them with a model name e.g. `original_model_name.rvt_upgraded_to_2019_.rvt` 
including an extension hinting at the version it was upgraded to.

Note that each model upgrade includes an audit performed by rvt. 
Existing model corruptions need to be resolved before being able to upgrade 
a rvt model.

## logs
All feedback of this process can be found in `rvt_model_services/logs`.
