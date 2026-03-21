#!/usr/bin/env python

"""Conditional override of Toyplot Axis rendering.

This preserves Toyplot defaults except when toytree sets custom attrs on
an Axis object to center the label on the spine-domain midpoint.
"""

import functools
from xml.etree import ElementTree as xml

import toyplot
from multipledispatch import dispatch
from toyplot.html import RenderContext, _axis_transform, _css_style, _draw_text

# Register multipledispatch to use the toyplot.html namespace.
dispatch = functools.partial(dispatch, namespace=toyplot.html._namespace)


@dispatch(toyplot.coordinates.Axis, RenderContext)
def _render(axis, context):
    if context.already_rendered(axis):
        return

    if not axis.show:
        return

    transform, length = _axis_transform(
        axis._x1, axis._y1, axis._x2, axis._y2, offset=axis._offset, return_length=True
    )

    axis_xml = xml.SubElement(
        context.parent,
        "g",
        id=context.get_id(axis),
        transform=transform,
        attrib={"class": "toyplot-coordinates-Axis"},
    )

    if axis.spine.show:
        x1 = 0
        x2 = length
        if (
            axis.domain.show
            and axis._data_min is not None
            and axis._data_max is not None
        ):
            x1 = max(x1, axis.projection(axis._data_min))
            x2 = min(x2, axis.projection(axis._data_max))
        xml.SubElement(
            axis_xml,
            "line",
            x1=repr(x1),
            y1=repr(0),
            x2=repr(x2),
            y2=repr(0),
            style=_css_style(axis.spine._style),
        )

        if axis.ticks.show:
            y1 = (
                axis._ticks_near
                if axis._tick_location == "below"
                else -axis._ticks_near
            )
            y2 = -axis._ticks_far if axis._tick_location == "below" else axis._ticks_far

            ticks_group = xml.SubElement(axis_xml, "g")
            for location, tick_style in zip(
                axis._tick_locations,
                axis.ticks.tick.styles(axis._tick_locations),
            ):
                x = axis.projection(location)
                xml.SubElement(
                    ticks_group,
                    "line",
                    x1=repr(x),
                    y1=repr(y1),
                    x2=repr(x),
                    y2=repr(y2),
                    style=_css_style(axis.ticks._style, tick_style),
                )

    if axis.ticks.labels.show:
        location = axis._tick_labels_location

        if axis.ticks.labels.angle:
            vertical_align = "middle"

            if location == "above":
                text_anchor = "start" if axis.ticks.labels.angle > 0 else "end"
            elif location == "below":
                text_anchor = "end" if axis.ticks.labels.angle > 0 else "start"
        else:
            vertical_align = "last-baseline" if location == "above" else "top"
            text_anchor = "middle"

        y = (
            axis._tick_labels_offset
            if location == "below"
            else -axis._tick_labels_offset
        )

        ticks_group = xml.SubElement(axis_xml, "g")
        for location, label, title, label_style in zip(
            axis._tick_locations,
            axis._tick_labels,
            axis._tick_titles,
            axis.ticks.labels.label.styles(axis._tick_locations),
        ):
            x = axis.projection(location)

            style = toyplot.style.combine(
                {
                    "-toyplot-vertical-align": vertical_align,
                    "text-anchor": text_anchor,
                },
                axis.ticks.labels.style,
                label_style,
            )

            _draw_text(
                root=ticks_group,
                text=label,
                x=x,
                y=y,
                style=style,
                angle=axis.ticks.labels.angle,
                title=title,
            )

    location = axis._label_location
    vertical_align = "last-baseline" if location == "above" else "top"
    text_anchor = "middle"
    y = axis._label_offset if location == "below" else -axis._label_offset

    # Default behavior is center label on full axis length. When toytree
    # marks this axis in spine-label mode, center on the data-domain span
    # rendered as the visible spine.
    x = length * 0.5
    if getattr(axis, "_toytree_label_mode", None) == "spine":
        midpoint = getattr(axis, "_toytree_label_data_midpoint", None)
        if midpoint is None:
            if axis._data_min is not None and axis._data_max is not None:
                midpoint = 0.5 * (axis._data_min + axis._data_max)
            elif axis._domain_min is not None and axis._domain_max is not None:
                midpoint = 0.5 * (axis._domain_min + axis._domain_max)
        if midpoint is not None:
            x = axis.projection(midpoint)
            x = min(max(x, 0), length)

    _draw_text(
        root=axis_xml,
        text=axis.label.text,
        x=x,
        y=y,
        style=toyplot.style.combine(
            {
                "-toyplot-vertical-align": vertical_align,
                "text-anchor": text_anchor,
            },
            axis.label.style,
        ),
    )

    if axis.interactive.coordinates.show:
        coordinates_xml = xml.SubElement(
            axis_xml,
            "g",
            attrib={"class": "toyplot-coordinates-Axis-coordinates"},
            style=_css_style({"visibility": "hidden"}),
            transform="",
        )

        if axis.interactive.coordinates.tick.show:
            y1 = (
                axis._tick_labels_offset
                if axis._interactive_coordinates_location == "below"
                else -axis._tick_labels_offset
            )
            y1 *= 0.5
            y2 = (
                -axis._tick_labels_offset
                if axis._interactive_coordinates_location == "below"
                else axis._tick_labels_offset
            )
            y2 *= 0.75
            xml.SubElement(
                coordinates_xml,
                "line",
                x1="0",
                x2="0",
                y1=repr(y1),
                y2=repr(y2),
                style=_css_style(axis.interactive.coordinates.tick.style),
            )

        if axis.interactive.coordinates.label.show:
            y = (
                axis._tick_labels_offset
                if axis._interactive_coordinates_location == "below"
                else -axis._tick_labels_offset
            )
            alignment_baseline = (
                "hanging"
                if axis._interactive_coordinates_location == "below"
                else "alphabetic"
            )
            xml.SubElement(
                coordinates_xml,
                "text",
                x="0",
                y=repr(y),
                style=_css_style(
                    toyplot.style.combine(
                        {"alignment-baseline": alignment_baseline},
                        axis.interactive.coordinates.label.style,
                    )
                ),
            )

    context.define(
        "toyplot.coordinates.Axis",
        ["toyplot/canvas"],
        """
        function(canvas)
        {
            function sign(x)
            {
                return x < 0 ? -1 : x > 0 ? 1 : 0;
            }

            function mix(a, b, amount)
            {
                return ((1.0 - amount) * a) + (amount * b);
            }

            function log(x, base)
            {
                return Math.log(Math.abs(x)) / Math.log(base);
            }

            function in_range(a, x, b)
            {
                var left = Math.min(a, b);
                var right = Math.max(a, b);
                return left <= x && x <= right;
            }

            function inside(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(in_range(segment.range.min, range, segment.range.max))
                        return true;
                }
                return false;
            }

            function to_domain(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(in_range(segment.range.bounds.min, range, segment.range.bounds.max))
                    {
                        if(segment.scale == "linear")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            return mix(segment.domain.min, segment.domain.max, amount)
                        }
                        else if(segment.scale[0] == "log")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            var base = segment.scale[1];
                            return sign(segment.domain.min) * Math.pow(base, mix(log(segment.domain.min, base), log(segment.domain.max, base), amount));
                        }
                    }
                }
            }

            var axes = {};

            function display_coordinates(e)
            {
                var current = canvas.createSVGPoint();
                current.x = e.clientX;
                current.y = e.clientY;

                for(var axis_id in axes)
                {
                    var axis = document.querySelector("#" + axis_id);
                    var coordinates = axis.querySelector(".toyplot-coordinates-Axis-coordinates");
                    if(coordinates)
                    {
                        var projection = axes[axis_id];
                        var local = current.matrixTransform(axis.getScreenCTM().inverse());
                        if(inside(local.x, projection))
                        {
                            var domain = to_domain(local.x, projection);
                            coordinates.style.visibility = "visible";
                            coordinates.setAttribute("transform", "translate(" + local.x + ")");
                            var text = coordinates.querySelector("text");
                            text.textContent = domain.toFixed(2);
                        }
                        else
                        {
                            coordinates.style.visibility= "hidden";
                        }
                    }
                }
            }

            canvas.addEventListener("click", display_coordinates);

            var module = {};
            module.show_coordinates = function(axis_id, projection)
            {
                axes[axis_id] = projection;
            }

            return module;
        }""",
    )

    projection = []
    for segment in axis.projection._segments:
        projection.append(
            {
                "scale": segment.scale,
                "domain": {
                    "min": segment.domain.min,
                    "max": segment.domain.max,
                    "bounds": {
                        "min": segment.domain.bounds.min,
                        "max": segment.domain.bounds.max,
                    },
                },
                "range": {
                    "min": segment.range.min,
                    "max": segment.range.max,
                    "bounds": {
                        "min": segment.range.bounds.min,
                        "max": segment.range.bounds.max,
                    },
                },
            }
        )

    context.require(
        dependencies=["toyplot.coordinates.Axis"],
        arguments=[context.get_id(axis), projection],
        code="""function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        }""",
    )
