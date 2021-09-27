# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-28 09:42

@author: johannes
"""
from functools import partial
from bokeh.models import Button, FileInput, CustomJS, CrosshairTool
from bokeh.layouts import row, Spacer
from bokeh.models.widgets import Select
from bokeh.plotting import figure
from bokeh.events import ButtonClick


def update_colormapper(fig=None, plot=None, color_mapper=None, data_source=None, x_sel=None):
    """Update the color map."""
    code = """
        var parameter = cb_obj.value;
        console.log('parameter', parameter);

        // var data = data_source.data;
        const {transform} = renderer.glyph.fill_color;

        transform.low = color_mapper[parameter].low;
        transform.high = color_mapper[parameter].high;

        console.log('transform.low', transform.low);
        console.log('transform.high', transform.high);

        renderer.glyph.fill_color = {field: parameter, transform: transform};
        fig.reset.emit()
    """
    return CustomJS(
        args=dict(fig=fig, renderer=plot, color_mapper=color_mapper,
                  data_source=data_source, x_sel=x_sel), 
        code=code)


def update_colormapper_transect(fig=None, plot=None, color_mapper=None):
    """Update the color map."""
    code = """
        var parameter = cb_obj.value;
        const {transform} = renderer.glyph.fill_color;
        var z = 'z';

        transform.low = color_mapper[parameter].low;
        transform.high = color_mapper[parameter].high;

        // console.log('transform.low', transform.low);
        // console.log('transform.high', transform.high);

        renderer.glyph.fill_color = {field: z, transform: transform};
        //renderer.glyph.fill_color = {field: 'z', transform: color_mapper[parameter]};
        //color_bar = color_mapper[parameter];
        //color_bar.trigger('change')
        fig.reset.emit()
    """
    return CustomJS(
        args=dict(fig=fig, renderer=plot, color_mapper=color_mapper), 
        code=code)


def update_colormapper_range(fig=None, plot=None, data_source=None):
    """Update the color map."""
    code = """
        var data = data_source.data;
        var parameter = cb_obj.value;
        const {transform} = renderer.glyph.fill_color;
        var z = 'z';

        transform.low = Math.min.apply(Math, data.z)-0.1;
        transform.high = Math.max.apply(Math, data.z)+0.1;

        renderer.glyph.fill_color = {field: z, transform: transform};
        fig.reset.emit()
    """
    return CustomJS(
        args=dict(fig=fig, renderer=plot, data_source=data_source), 
        code=code)


def select_callback(data_source=None, axis_objs=None, axis=None):
    """Return JS callback select object."""
    code = """
    var selector_parameter = this.value;
    var data = data_source.data; 
    var axis_objs = axis_objs;

    if (axis == 'x') {
        data['x'] = data[selector_parameter];
    } else if (axis == 'y') {
        data['y'] = data[selector_parameter];
    }
    for (var i = 0; i < axis_objs.length; i++) {
        axis_objs[i].axis_label = selector_parameter
    }

    data_source.selected.indices = [];
    data_source.change.emit();
    """
    return CustomJS(
        code=code,
        args={'data_source': data_source,
              'axis_objs': axis_objs,
              'axis': axis}
    )


def lasso_callback(x_selector=None, y_selector=None, data_source=None, corr_source=None):
    """Return JS callback lasso object."""
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


def lasso_transect_callback(z_selector=None,     
                            pos_source=None,
                            data_source=None,
                            plot_source=None):
    """Return JS callback lasso object."""
    code = """
    var x_param = 'timestamp';
    var y_param = 'PRES_CTD';
    var z_param = z_selector.value;
    var time_param = 'timestring';

    var data = data_source.data;
    var pos = pos_source.data;

    var new_data = {x: [], y: [], z: []};
    var pos_indices = pos_source.selected.indices;
    
    var selected_keys = [];
    for (var i = 0; i < pos_indices.length; i++) {
        selected_keys.push(pos[time_param][pos_indices[i]]);
    }

    var x_val, y_val, z_val, time_val; 
    for (var i = 0; i < data.x.length; i++) {
        time_val = data[time_param][i];
        
        if (selected_keys.indexOf(time_val) !== -1) {
            x_val = data[x_param][i];
            y_val = data[y_param][i];
            z_val = data[z_param][i];
            new_data.x.push(x_val);
            new_data.y.push(y_val);
            new_data.z.push(z_val);
        }
    }
    plot_source.data = new_data;
    """
    return CustomJS(args=dict(
        z_selector=z_selector,
        pos_source=pos_source,
        data_source=data_source,
        plot_source=plot_source,
        ),
        code=code)


def lasso_corr_callback(x_selector=None, y_selector=None, data_source=None, 
                        position_source=None, corr_source=None, corr_plot=None):
    """Return JS callback lasso object."""
    code = """
    console.log('lasso_callback');

    var x_param = x_selector.value;
    var y_param = y_selector.value;

    var data = data_source.data;
    var pos_data = position_source.data;
    var new_data = {x: [], y: [], dep: [], key: []};

    var indices = cb_obj.indices;
    var selected_keys = [];

    for (var i = 0; i < indices.length; i++) {
        selected_keys.push(pos_data['KEY'][indices[i]]);
    }

    var key_val, x_val, y_val, dep_val;
    for (var i = 0; i < data.KEY.length; i++) {
        key_val = data.KEY[i];

        if (selected_keys.indexOf(key_val) !== -1) {
            x_val = data[x_param][i];
            y_val = data[y_param][i];
            dep_val = data['DEPH'][i];
            new_data.x.push(x_val);
            new_data.y.push(y_val);
            new_data.dep.push(dep_val);
            new_data.key.push(key_val);
        }
    }
    if (new_data.x.length > 1) {
        //console.log('axes_range update!', corr_plot.x_range.start, corr_plot.x_range.end, corr_plot.y_range.start, corr_plot.y_range.end)
        var min_value = Math.min(...new_data.x.filter(x => !Number.isNaN(x)), ...new_data.y.filter(x => !Number.isNaN(x)))-0.2;
        var max_value = Math.max(...new_data.x.filter(x => !Number.isNaN(x)), ...new_data.y.filter(x => !Number.isNaN(x)))+0.2;
        corr_plot.x_range.start = min_value;
        corr_plot.x_range.end = max_value;            
        corr_plot.y_range.start = min_value;
        corr_plot.y_range.end = max_value;
        corr_plot.change.emit();
        corr_plot.reset.emit();
        //console.log('after update!', corr_plot.x_range.start, corr_plot.x_range.end, corr_plot.y_range.start, corr_plot.y_range.end)
    }
    corr_source.data = new_data;
    """
    return CustomJS(args=dict(
        x_selector=x_selector, 
        y_selector=y_selector, 
        data_source=data_source, 
        position_source=position_source,
        corr_source=corr_source,
        corr_plot=corr_plot,
        ),
        code=code)


def range_selection_callback(data_source=None):
    """Return JS callback select object."""
    code = """
    var data = data_source.data;
    var min_dep = cb_obj.value[0];
    var max_dep = cb_obj.value[1];
    var indices = [];
    for (var i = 0; i < data.dep.length; i++) {
        if ((data.dep[i] >= min_dep) && (data.dep[i] <= max_dep)) {
            indices.push(i)
        }
    }
    data_source.selected.indices = indices;
    """
    return CustomJS(args={'data_source': data_source},
                    code=code)


def range_slider_update_callback(slider=None, data_source=None):
    """Return JS callback slider object."""
    code = """
    var data = data_source.data;        
    //var values = [];
    //var i = 0;
    //while ( ! isNaN(data.y[i]) ) {
    //    values.push(data.y[i])
    //    i++
    //}
    slider.start = Math.min.apply(Math, data.dep);
    slider.end = Math.max.apply(Math, data.dep);
    slider.value = [slider.start, slider.end];
    slider.change.emit();
    """
    return CustomJS(args={'slider': slider, 'data_source': data_source},
                    code=code)


def month_selection_callback(position_source=None, position_master_source=None):
    """Return JS callback select object."""
    code = """
    console.log('month_selection_callback');
    // Get data from ColumnDataSource
    var selected_data = {LATIT: [], LONGI: [], STATN: [], KEY: [], MONTH: []};
    var master = master_source.data;

    var month_mapping = {'All': 'All',
                         'January': 1, 'February': 2,
                         'March': 3, 'April': 4,
                         'May': 5, 'June': 6,
                         'July': 7, 'August': 8,
                         'September': 9, 'October': 10,
                         'November': 11, 'December': 12};

    var selected_month = month_mapping[month.value];

    var key_val, lat_val, lon_val, statn_val, mon_val;
    for (var i = 0; i < master.KEY.length; i++) {
        key_val = master.KEY[i];
        lat_val = master.LATIT[i];
        lon_val = master.LONGI[i];
        statn_val = master.STATN[i];
        mon_val = master.MONTH[i];

        if (selected_month == 'All') {
            selected_data.KEY.push(key_val);
            selected_data.LATIT.push(lat_val);
            selected_data.LONGI.push(lon_val);
            selected_data.STATN.push(statn_val);
            selected_data.MONTH.push(mon_val);
        } else if (mon_val == selected_month) {
            selected_data.KEY.push(key_val);
            selected_data.LATIT.push(lat_val);
            selected_data.LONGI.push(lon_val);
            selected_data.STATN.push(statn_val);
            selected_data.MONTH.push(mon_val);
        }
    }

    source.data = selected_data;
    """
    # Create a CustomJS callback with the code and the data
    return CustomJS(args={'source': position_source,
                          'master_source': position_master_source},
                    code=code)


def lasso_correlation_callback(z_selector=None,     
                               pos_source=None,
                               data_source=None,
                               plot_source=None,
                               line_source=None):
    """Return JS callback lasso object."""
    code = """
    var mapper = {'DOXY_CTD': 'DOXY_MVP', 'DENS_CTD': 'DENS_MVP'};
    var time_param = 'timestring';
    var selected_param = z_selector.value;
    var selected_param_mvp = mapper[selected_param];

    var data = data_source.data;
    var pos = pos_source.data;

    var pos_indices = pos_source.selected.indices;
    
    var selected_keys = [];
    for (var i = 0; i < pos_indices.length; i++) {
        selected_keys.push(pos[time_param][pos_indices[i]]);
    }

    var new_data = {x: [], y: []};

    var x_val, y_val, time_val; 
    for (var i = 0; i < data.PRES_CTD.length; i++) {
        time_val = data[time_param][i];
        
        if (selected_keys.indexOf(time_val) !== -1) {
            x_val = data[selected_param][i];
            y_val = data[selected_param_mvp][i];
            new_data.x.push(x_val);
            new_data.y.push(y_val);
        }
    }

    var high = Math.max.apply(Math, [Math.max.apply(Math, new_data.x), Math.max.apply(Math, new_data.y)]);
    var low = Math.min.apply(Math, [Math.min.apply(Math, new_data.x), Math.min.apply(Math, new_data.y)]);
    line_source.data = {x: [low, high], y: [low, high]};

    plot_source.data = new_data;
    """
    return CustomJS(args=dict(
        z_selector=z_selector,
        pos_source=pos_source,
        data_source=data_source,
        plot_source=plot_source,
        line_source=line_source,
        ),
        code=code)
