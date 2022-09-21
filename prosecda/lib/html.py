import os
import shutil

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from .. import html  # relative-import the *package* containing the templates


def get_html_path():
    template = pkg_resources.read_text(html, 'index.html')
    with pkg_resources.path(html, "index.html") as p:
        html_path = os.path.dirname(p)

    return html_path


def generate_html(outdir: str):
    html_files = [
        ('/index.html', ''),
        ('/css/style.css', 'css/'), 
        ('/js/d3.v6.min.js', 'js/'),
        ('/js/d3_script.js', 'js/'),
        ('/images/i2bc.jpg', 'images/'),
        ]

    html_path = get_html_path()

    # create js/ and css/ directory in outdir
    os.makedirs(outdir + '/js/', exist_ok=True)
    os.makedirs(outdir + '/css/', exist_ok=True)
    os.makedirs(outdir + '/images/', exist_ok=True)


    # copy index.html, js/ css/ in outdir
    for _file, dest in html_files:
        source = html_path + _file
        if os.path.isfile(source):
            # print(source, outdir + dest)
            shutil.copy(source, outdir + dest)


