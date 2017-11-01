import rjm


def cmd_journal(project_code, model_path, jrn_path, com_dir, log_dir):
    rvt_jrn = rjm.JournalMaker(permissive=False)
    rvt_jrn.open_workshared_model(model_path=model_path, detached=True, audit=True)
    rvt_jrn.close_model()
    rvt_jrn.write_journal(jrn_path)


register = {"name": "audit",
            "rjm": cmd_journal,
            }
