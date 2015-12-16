# Copyright (c) 2015  aggftw@gmail.com
# Distributed under the terms of the Modified BSD License.

import pandas as pd
from ipywidgets import FlexBox
from IPython.display import display

from .encoding import Encoding
from .encodingwidget import EncodingWidget
from .ipywidgetfactory import IpyWidgetFactory


class IpythonDisplay(object):
    @staticmethod
    def display_to_ipython(to_display):
        display(to_display)


class AutoVizWidgetTest(FlexBox):
    """This class should not be used by anyone outside of the project. People should use AutoVizWidget instead.
    This class is here for testing purposes."""
    def __init__(self, df, encoding, renderer, ipywidget_factory, encoding_widget, ipython_display,
                 nested_widget_mode=False, testing=False, **kwargs):
        assert encoding is not None
        assert df is not None
        assert type(df) is pd.DataFrame
        assert len(df.columns) > 0
        assert renderer is not None
        assert ipywidget_factory is not None

        kwargs['orientation'] = 'vertical'

        if not testing:
            super(AutoVizWidgetTest, self).__init__((), **kwargs)

        self.ipywidget_factory = ipywidget_factory
        self.encoding_widget = encoding_widget

        self.df = df
        self.encoding = encoding
        self.renderer = renderer
        self.ipython_display = ipython_display

        # Widget that will become the only child of AutoVizWidget
        self.widget = self.ipywidget_factory.get_vbox()

        # Create output area
        self.to_display = self.ipywidget_factory.get_output()
        self.to_display.width = "800px"
        self.output = self.ipywidget_factory.get_hbox()
        self.output.children = [self.to_display]

        self.controls = self._create_controls_widget()

        if nested_widget_mode:
            self.widget.children = [self.controls, self.output]
            self.children = [self.widget]
        else:
            self.ipython_display.display(self.controls)
            self.ipython_display.display(self.to_display)

        self.on_render_viz()

    def on_render_viz(self, *args):
        # self.controls.children
        self.to_display.clear_output()

        self.renderer.render(self.df, self.encoding, self.to_display)

        self.encoding_widget.show_x(self.renderer.display_x(self.encoding.chart_type))
        self.encoding_widget.show_y(self.renderer.display_y(self.encoding.chart_type))
        self.encoding_widget.show_controls(self.renderer.display_controls(self.encoding.chart_type))
        self.encoding_widget.show_logarithmic_x_axis(self.renderer.display_logarithmic_x_axis(self.encoding.chart_type))
        self.encoding_widget.show_logarithmic_y_axis(self.renderer.display_logarithmic_y_axis(self.encoding.chart_type))

    def _create_controls_widget(self):
        # Create types of viz hbox
        viz_types_widget = self._create_viz_types_buttons()

        controls = self.ipywidget_factory.get_vbox()
        controls.children = [viz_types_widget, self.encoding_widget]

        return controls

    def _create_viz_types_buttons(self):
        hbox = self.ipywidget_factory.get_hbox()
        children = list()

        self.heading = self.ipywidget_factory.get_html('Type:', width='80px', height='32px')
        children.append(self.heading)

        self._create_type_button(Encoding.chart_type_table, children)
        self._create_type_button(Encoding.chart_type_pie, children)

        if len(self.df.columns) > 1:
            self._create_type_button(Encoding.chart_type_line, children)
            self._create_type_button(Encoding.chart_type_area, children)
            self._create_type_button(Encoding.chart_type_bar, children)

        hbox.children = children

        return hbox

    def _create_type_button(self, name, children):
        def on_render(*args):
            self.encoding.chart_type = name
            return self.on_render_viz()

        button = self.ipywidget_factory.get_button(description=name)
        button.padding = "10px"
        button.on_click(on_render)

        children.append(button)


class AutoVizWidget(AutoVizWidgetTest):
    def __init__(self, df, encoding, renderer, nested_widget_mode=False, **kwargs):
        encoding_widget = EncodingWidget(self.df, self.encoding, self.on_render_viz)

        super(AutoVizWidgetTest, self).__init__((df, encoding, renderer, IpyWidgetFactory(), encoding_widget,
                                                 IpythonDisplay(), nested_widget_mode), **kwargs)
