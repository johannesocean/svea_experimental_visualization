from functools import partial
from bokeh.models import Button, FileInput, CustomJS, CrosshairTool
from bokeh.layouts import row, Spacer
from bokeh.models.widgets import Select
from bokeh.plotting import figure
from bokeh.events import ButtonClick


def update_colormapper(figure=None, plot=None, color_mapper=None, data_source=None, x_sel=None):
    code="""
        var parameter = cb_obj.value;
        console.log('parameter', parameter);
        var data = data_source.data;
        const {transform} = renderer.glyph.fill_color;

        transform.low = color_mapper[parameter].low;
        transform.high = color_mapper[parameter].high;

        // console.log('transform.low', transform.low);
        // console.log('transform.high', transform.high);

        renderer.glyph.fill_color = {field: parameter, transform: transform};
        p.reset.emit()
    """
    return CustomJS(
        args=dict(p=figure, renderer=plot, color_mapper=color_mapper, 
                  data_source=data_source, x_sel=x_sel), 
        code=code)



def select_callback(data_source=None, axis_obj=None, axis=None):
    code = """
    var selector_parameter = this.value;
    var data = data_source.data; 
    var axis_obj = axis_obj;

    if (axis == 'x') {
        axis_obj.axis_label = selector_parameter
        data['x'] = data[selector_parameter];
    } else if (axis == 'y') {
        axis_obj.axis_label = selector_parameter
        data['y'] = data[selector_parameter];
    }   
    data_source.change.emit();
    """
    return CustomJS(
        code=code,
        args={'data_source': data_source,
              'axis_obj': axis_obj,
              'axis': axis}
    )


def lasso_callback(x_selector=None, y_selector=None, data_source=None, corr_source=None):
    """"""
    code = """
    console.log('lasso_callback');

    var x_param = x_selector.value;
    var y_param = y_selector.value;

    var data = data_source.data;

    var new_data = {x: [], y: []};
    var indices = data_source.selected.indices;

    var x_val, y_val;
    for (var i = 0; i < indices.length; i++) {
        x_val = data[x_param][indices[i]];
        y_val = data[y_param][indices[i]];

        new_data.x.push(x_val);
        new_data.y.push(y_val);
    }
    corr_source.data = new_data;
    """
    return CustomJS(args=dict(
        x_selector=x_selector, 
        y_selector=y_selector, 
        data_source=data_source, 
        corr_source=corr_source
        ),
        code=code)
