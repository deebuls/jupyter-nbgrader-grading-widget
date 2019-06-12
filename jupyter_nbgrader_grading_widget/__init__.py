from ._version import version_info, __version__

#from .example import *
from .grading_widget import *

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'jupyter-nbgrader-grading-widget',
        'require': 'jupyter-nbgrader-grading-widget/extension'
    }]
