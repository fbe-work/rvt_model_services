## cookiecutter template

this is a template for a custom command. On its own it basically does not mode than running the same actions as a audit. It does it with all currently possible overrides to show what is possible:<br>
    * you can override the template of the journal that controls rvt:
        register: override_jrn_template
    * you can override also just the command part of the journal:
        register: override_jrn_template
    * you can override the addin to control which plugins get loaded to rvt:
        register: override_addin_template
    * you can provide with custom python modules that can be run post process:<br>
        example: cookie.py
