# command: sync_benchmark

## command description
`sync_benchmark` will gather some machine stats and perform 
detach-open, sync, close 10 times on the specified model.

In `rvt_model_services/logs` one will not only find the regular log, 
but also two csvs:
* `COMPUTERNAME_prjnumber_sb_benchmark_.csv` <br>
    with the stats and the average timing.
* `COMPUTERNAME_prjnumber_sb_benchmark__single_iteration.csv`
    the individual sync timings.

## typical invocation
`python process_model.py sync_benchmark 123_sync "C:\temp\123\123_benchmark.rvt"  --timeout
=99999`

## logs
All feedback of this process can be found in `rvt_model_services/logs`.
