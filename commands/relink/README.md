# command: relink

## command description
`relink` will search through the directory in which the rvt model is located, 
that got specified when running the command and process each workshared or 
standalone rvt model in there. 
A mapping needs to be provided in this directory named: `relink_map.json`.
With the following content:
```
{
  "rvt": {
    "link_same_dir.rvt"       : ""
    "link_nested.rvt"         : "..\\02_LINKED\\00_SITE\\",
    "partly_matched_link_name": "..\\02_LINKED\\15_STR\\"
  },
  "cad": {
    "link_same_dir.dwg"       : "",
    "link_nested.dwg"         : "..\\02_LINKED\\00_SITE\\",
    "partly_matched_link_name": "..\\02_LINKED\\15_STR\\"
  }
}
```
It will list all the linked rvt and cad (dwg, sat) files in per model, 
and will relink them according to the `relink_map.json` if it happens to match.

Note that this will only have an effect on models, that are in transmitted state, 
e.g. an eTransmitted rvt model.

## logs
All feedback of this process can be found in `rvt_model_services/logs`.
