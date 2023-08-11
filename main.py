import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, Text, CustomJS, Block, HoverTool, Range1d
from bokeh import events
from datetime import datetime as dt, timedelta as td


focus_color={
    "politics": "lightgray",
    "marine": "lightblue",
    "economy": "bisque"}



vanilla = pd.read_csv("NSB_original.csv", index_col=0)

starts = []
for i, duration in enumerate(vanilla["Start"]):
    if not pd.isna(vanilla.loc[i, "Start"]):
        starts.append(dt.fromisoformat(vanilla.loc[i, "Start"]))
    else:
        starts.append(starts[-1]+td(days=vanilla.loc[i-1, "Duration"]))
date_range = []
for i, start in enumerate(starts):
    date_range.append(start.isoformat()[:10] + " to " + (start + td(days=vanilla.loc[i, "Duration"])).isoformat()[:10])
ys = vanilla["Y"]

p = figure(width_policy="max",
           width=800,
           height=600,
           tools="pan, wheel_zoom, reset",
           x_axis_type="datetime")
p.y_range = Range1d(-4, 4)
p.x_range = Range1d(starts[0] - td(days=1), starts[0] + td(days=2*365.25))

original_size = p.x_range.end - p.x_range.start
length35 = td(days=35)


focuses = vanilla["Focus"]
focuses = ["\n".join(focus.split()) for focus in focuses]
vanilla_source = ColumnDataSource({
    "x": starts,
    "y": ys,
    "width": [td(days=duration) for duration in vanilla["Duration"]],
    "height": [0.9]*len(vanilla),
    "color": [focus_color[focus_type] for focus_type in vanilla["Type"]],
    "focus": focuses,
    "hover_text": vanilla["Hovertext"],
    "text_font": ["courier"]*len(vanilla),
    "date_range" : date_range
    })

glyph_block = Block(
    x="x",
    y="y",
    width="width",
    height="height",
    fill_color="color")

font_size = int(length35 / original_size * p.width / 14 * 2 * 1.6);
glyph_text = Text(
    x="x",
    y="y",
    text="focus",
    text_font_size = f"{font_size}px",
    text_font = "text_font")

block_renderer = p.add_glyph(vanilla_source, glyph_block)
text_renderer = p.add_glyph(vanilla_source, glyph_text)


callback_scaling_text = CustomJS(args=dict(
        glyph_text=glyph_text,
        original_size=original_size,
        p=p,
        font_size=font_size),
    code="""
const new_size = Math.floor(original_size / (p.x_range.end - p.x_range.start)  * font_size);
glyph_text.text_font_size = new_size + "px";
""")
p.x_range.js_on_change('end', callback_scaling_text)
p.x_range.js_on_change('start', callback_scaling_text)

block_hover = HoverTool(renderers=[block_renderer], tooltips=[("", "@focus"),
                                                              ("", "@date_range"),
                                                              ("", "@hover_text")])
p.add_tools(block_hover)

p.toolbar.active_scroll = "auto"

show(p)
