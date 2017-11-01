## cookiecutter template

this is a template for a custom command.<br>
On its own it basically does not more than running the same actions as a audit.<br>
It does it with all currently possible overrides to show what is possible:<br>

* you can override the template of the journal that controls rvt:<br>
     register: override_jrn_template<br>
* you can override also just the command part of the journal:<br>
     register: override_jrn_template<br>
* you can override the addin to control which plugins get loaded to rvt:<br>
     register: override_addin_template<br>
* you can provide with custom python modules that can be run post process:<br>
     cookie.py<br>
