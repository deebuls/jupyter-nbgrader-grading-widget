var jupyter-nbgrader-grading-widget = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'jupyter-nbgrader-grading-widget',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'jupyter-nbgrader-grading-widget',
          version: jupyter-nbgrader-grading-widget.version,
          exports: jupyter-nbgrader-grading-widget
      });
  },
  autoStart: true
};

