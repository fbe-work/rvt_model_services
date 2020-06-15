# command: relink

## command description
`relink` will search through the directory, in which the rvt model is located, 
that got specified when running the command and process each workshared or 
standalone rvt model in there. 

A mapping needs to be provided in this directory: `relink_map.json`.<br>
Example content:
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
`relink` will list all the linked rvt and cad (dwg, sat) files in per model.
If links happen to match they will be relinked them according to the 
`relink_map.json`. <br>
The example mapping shows rvt/dwg files with the specific name matching 
`link_same_dir.rvt`/`link_same_dir.dwg`, that are linked to the same directory. 
Links `link_nested.rvt`/`link_nested.dwg` specifically matching, and rvt/dwg 
with only partly matching file names `partly_matched_link_name`, 
that reside one directory up and from there two directories nested, 
in `02_LINKED` and `15_STR`.

Note that this will only have an effect on models, that are in transmitted state, 
e.g. an eTransmitted rvt model.

## logs
All feedback of this process can be found in `rvt_model_services/logs`.
