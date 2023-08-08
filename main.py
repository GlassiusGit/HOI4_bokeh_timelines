import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, Text, CustomJS, Block, HoverTool, Range1d
from bokeh import events
from datetime import datetime as dt, timedelta as td

vanilla = pd.read_csv("NSB_original.csv", index_col=0)

focus_color={
    "politics": "lightgray",
    "marine": "lightblue",
    "economy": "bisque"}

starts = [dt(1936, 1, 1)]
for duration in vanilla["Duration"][:-1]:
    starts.append(starts[-1]+td(days=duration))

focuses = vanilla["Focus"]
focuses = ["\n".join(focus.split()) for focus in focuses]
vanilla_source = ColumnDataSource({
    "x": starts,
    "y":[1]*len(vanilla),
    "width": [td(days=duration) for duration in vanilla["Duration"]],
    "height": [1.4]*len(vanilla),
    "color": [focus_color[focus_type] for focus_type in vanilla["Type"]],
    "focus": focuses,
    "hover_text": vanilla["Hovertext"],
    })

glyph_block = Block(
    x="x",
    y="y",
    width="width",
    height="height",
    fill_color="color")
glyph_text = Text(
    x="x",
    y="y",
    text="focus")

p = figure(width_policy="max",
           width=800,
           height=600,
           tools="pan, wheel_zoom, reset",
           x_axis_type="datetime")
p.y_range = Range1d(-4, 2.6)
p.x_range = Range1d(dt(1935, 12, 31), dt(1937,12,1))

block_renderer = p.add_glyph(vanilla_source, glyph_block)
text_renderer = p.add_glyph(vanilla_source, glyph_text)

original_size = max(starts)-min(starts)
callback_scaling_text = CustomJS(args=dict(glyph_text=glyph_text, original_size=original_size, p=p), code="""
    const new_size = Math.floor(original_size / (p.x_range.end - p.x_range.start)  * 6);
    glyph_text.text_font_size = new_size + "px";
""")
p.x_range.js_on_change('end', callback_scaling_text)
p.x_range.js_on_change('start', callback_scaling_text)

block_hover = HoverTool(renderers=[block_renderer], tooltips=[("", "@hover_text")])
p.add_tools(block_hover)

p.toolbar.active_scroll = "auto"

show(p)
