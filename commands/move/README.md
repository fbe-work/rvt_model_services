# command: move

## command description
`move` will search through the directory, in which the rvt model is located, 
that got specified when running the command and process each workshared or 
standalone rvt model in there. 

A mapping needs to be provided in this directory: `move_models.json`.<br>
Example content:
```
{
  "C:/source/model_01.rvt_upgraded_to_2017_.rvt":  "C:/target/model_01.rvt",	
  "C:/source/model_02.rvt_upgraded_to_2017_.rvt":  "C:/target/nested/model_02.rvt"
}
```
If model links happen to match, they will be moved according to the 
`move_models.json` mapping, as specified: **source_path:target_path** 

## logs
All feedback of this process can be found in `rvt_model_services/logs`.
