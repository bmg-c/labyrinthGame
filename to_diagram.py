# import erdantic as erd
# from erdantic.examples.pydantic import Party
#
# # Easy one-liner
# erd.draw(from, out="diagram.png")

from py2puml.py2puml import py2puml
path_out = "diagram.puml"
domain_name = 'app'
domain_module = 'app'
print(''.join(py2puml(domain_name, domain_module)))

with open(path_out, 'w') as puml_file:
    puml_file.writelines(py2puml(domain_name, domain_module))