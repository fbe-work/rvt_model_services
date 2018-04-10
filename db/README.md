## rvt_model_services db

this is the directory, where rvt_model_services will write the job_db.
rms jobs are each stored into json tinydb ("jobs.json") as follows:

{'<command>': 'rps_audit',
 '<full_model_path>': 'd:/test/123_N.rvt',
 '<project_code>': '123_N',
 '>start_time': '12:15:00',
 'notify': True,
 'timeout': 180,
 'viewer': True}
