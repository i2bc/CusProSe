
import jinja2
from jinja2 import Environment, PackageLoader, select_autoescape
import os

path=os.path.abspath(os.getcwd())+'/prosecda/html/templates'

template_loader = jinja2.FileSystemLoader(searchpath="templates/")
# template_loader = jinja2.FileSystemLoader(searchpath=path)

template_env = jinja2.Environment(loader=template_loader)

# print(template_env.list_templates())
template = template_env.get_template('index.jinja.html')

datas = [
    {'start': '110', 'length': '500'},
    {'start': '250', 'length': '700'},
    {'start': '650', 'length': '125'}
    ]

with open('index.html', 'w') as _file:
    _file.write(template.render(datas=datas))