import ipywidgets as widgets
from traitlets import Unicode

@widgets.register
class GradingWidget(widgets.DOMWidget):
    """An example widget."""
    _view_name = Unicode('GradingView').tag(sync=True)
    _model_name = Unicode('GradingModel').tag(sync=True)
    _view_module = Unicode('jupyter-nbgrader-grading-widget').tag(sync=True)
    _model_module = Unicode('jupyter-nbgrader-grading-widget').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    value = Unicode('Hello World!').tag(sync=True)
    question = Unicode('Question ').tag(sync=True)
    answer = Unicode('Answer').tag(sync=True)

    def clear(self):
        self.question = ""
        self.answer = ""
