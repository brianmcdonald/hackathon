#!/usr/bin/env python
# coding: utf-8

import polars as pl
import geopandas as gpd
from itables import init_notebook_mode, show
import pydeck as pdk
import hvplot
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import dates
from matplotlib.dates import DateFormatter
from datetime import datetime
from scipy.interpolate import CubicSpline
from scipy import interpolate
import numpy as np
from lonboard import Map, SolidPolygonLayer

df1 = pl.read_csv("input/24468477373345527_2024-06-30_2024-07-10_csv/*.csv", infer_schema_length=0)
df2 = pl.read_csv("input/1491089458459788_2024-07-03_2024-07-10_csv/*.csv", infer_schema_length=0)
df = pl.concat([df1, df2])

df = df.with_columns([
    pl.col("date_time").str.strptime(pl.Datetime, '%Y-%m-%d %H:%M'),
]).with_columns([
    pl.col("date_time").dt.date().alias("date"),
    pl.col("date_time").dt.time().alias("time"),
    pl.col("n_baseline").cast(pl.Float32, strict=False),
    pl.col("n_crisis").cast(pl.Float32, strict=False),
    pl.col("n_difference").cast(pl.Float32, strict=False),
]).group_by(['latitude', 'longitude','quadkey','date']).agg([ pl.mean('n_baseline').alias('mean_n_baseline'),pl.mean('n_crisis').alias('mean_n_crisis'),pl.mean('n_difference').alias('mean_n_difference')])
df = df.drop_nulls().with_columns(((pl.col('mean_n_crisis') - pl.col('mean_n_baseline'))*100/pl.col('mean_n_baseline')).alias('mean_percentage_change'))

day = "2024-07-09"
day = datetime.strptime(day, '%Y-%m-%d')
df_filtered = df.filter(pl.col('date')==day)

landfall_day = "2024-07-01"
landfall_day = datetime.strptime(landfall_day, '%Y-%m-%d')
landfall_df_filtered = df.filter(pl.col('date')==landfall_day)

cyclone_track = gpd.read_file('./input/track.geojson')
current_position = gpd.read_file('./input/position.geojson')

# current
map=df_filtered.with_columns(
    pl.when(pl.col("mean_percentage_change") < -30)
    .then(215)
    .when(pl.col("mean_percentage_change") <  -10)
    .then(253)
    .when(pl.col("mean_percentage_change") > 30)
    .then(43)
    .when(pl.col("mean_percentage_change") > 10)
    .then(171)
    .otherwise(255)
    .alias("R")
).with_columns(
    pl.when(pl.col("mean_percentage_change") < -30)
    .then(25)
    .when(pl.col("mean_percentage_change") <  -10)
    .then(174)
    .when(pl.col("mean_percentage_change") > 30)
    .then(131)
    .when(pl.col("mean_percentage_change") > 10)
    .then(221)
    .otherwise(255)
    .alias("G")
).with_columns(
    pl.when(pl.col("mean_percentage_change") < -30)
    .then(28)
    .when(pl.col("mean_percentage_change") <  -10)
    .then(97)
    .when(pl.col("mean_percentage_change") > 30)
    .then(186)
    .when(pl.col("mean_percentage_change") > 10)
    .then(164)
    .otherwise(191)
    .alias("B")
).with_columns(pl.col("mean_percentage_change").round(0)).to_pandas()

pop = pdk.Layer(
    'QuadkeyLayer',  
    map,
    get_tile='quadkey',
    getQuadkey = 'quadkey',
    pickable=True,
    get_fill_color="[R, G, B, 200]",
    auto_highlight=True
)

cyclone = pdk.Layer(
    "GeoJsonLayer",
    cyclone_track,
    opacity=0.9,
    stroked=True,
    width_min_pixels=10,
    filled=True,
    auto_highlight=True,
    pickable=True,
    get_fill_color=[243, 118, 38],
    get_line_color=[243, 118, 38],
    getLineWidth=500,
)

position = pdk.Layer(
    "GeoJsonLayer",
    current_position,
    opacity=1,
    stroked=True,
    width_min_pixels=30,
    filled=True,
    auto_highlight=True,
    pickable=True,
    get_radius=20000,
    get_fill_color=[243, 118, 38],
)

view_state = pdk.ViewState(
    longitude=-61.704712,
    latitude=12.331952,
    zoom=7,  # Adjust the zoom level to your preference
    pitch=0
)


r = pdk.Deck(layers=[pop, cyclone, position], initial_view_state=view_state, tooltip={"text": "% population change: {mean_percentage_change},"})
r.to_html('outputs/map.html')

# landfall map
map=landfall_df_filtered.with_columns(
    pl.when(pl.col("mean_percentage_change") < -30)
    .then(215)
    .when(pl.col("mean_percentage_change") <  -10)
    .then(253)
    .when(pl.col("mean_percentage_change") > 30)
    .then(43)
    .when(pl.col("mean_percentage_change") > 10)
    .then(171)
    .otherwise(255)
    .alias("R")
).with_columns(
    pl.when(pl.col("mean_percentage_change") < -30)
    .then(25)
    .when(pl.col("mean_percentage_change") <  -10)
    .then(174)
    .when(pl.col("mean_percentage_change") > 30)
    .then(131)
    .when(pl.col("mean_percentage_change") > 10)
    .then(221)
    .otherwise(255)
    .alias("G")
).with_columns(
    pl.when(pl.col("mean_percentage_change") < -30)
    .then(28)
    .when(pl.col("mean_percentage_change") <  -10)
    .then(97)
    .when(pl.col("mean_percentage_change") > 30)
    .then(186)
    .when(pl.col("mean_percentage_change") > 10)
    .then(164)
    .otherwise(191)
    .alias("B")
).with_columns(pl.col("mean_percentage_change").round(0)).to_pandas()

pop = pdk.Layer(
    'QuadkeyLayer',  
    map,
    get_tile='quadkey',
    getQuadkey = 'quadkey',
    pickable=True,
    get_fill_color="[R, G, B, 200]",
    auto_highlight=True
)

cyclone = pdk.Layer(
    "GeoJsonLayer",
    cyclone_track,
    opacity=0.9,
    stroked=True,
    width_min_pixels=10,
    filled=True,
    auto_highlight=True,
    pickable=True,
    get_fill_color=[243, 118, 38],
    get_line_color=[243, 118, 38],
    getLineWidth=500,
)

position = pdk.Layer(
    "GeoJsonLayer",
    current_position,
    opacity=1,
    stroked=True,
    width_min_pixels=30,
    filled=True,
    auto_highlight=True,
    pickable=True,
    get_radius=20000,
    get_fill_color=[243, 118, 38],
)

view_state = pdk.ViewState(
    longitude=-61.704712,
    latitude=12.331952,
    zoom=7,  # Adjust the zoom level to your preference
    pitch=0
)


r = pdk.Deck(layers=[pop, cyclone, position], initial_view_state=view_state, tooltip={"text": "% population change: {mean_percentage_change},"})
r.to_html('outputs/landfall-map.html')

city_name = 'Hillsborough'
hillsborough = ["03230322010032", "03230322010033"]
city = df.filter(pl.col('quadkey').is_in(hillsborough))

city_grouped = (
    city
    .group_by(['date'])
    .agg([
        pl.sum('mean_n_baseline').alias('baseline'),
        pl.sum('mean_n_crisis').alias('crisis')
    ]).with_columns([
            ((pl.col('crisis')-pl.col('baseline'))*100/pl.col('baseline')).round(0).alias('percent_change'),
        ])
).sort(by ='date')

dates = mpl.dates.date2num(city_grouped['date'].to_list())
cs = CubicSpline(dates, city_grouped['percent_change'].to_list())
dates_new = np.linspace(dates.min(), dates.max(), 300)
smooth_line = cs(dates_new)
dates_smooth = mpl.dates.num2date(dates_new)


fig, ax = plt.subplots(figsize=(5,3), tight_layout=True)
ax.plot(city_grouped['date'], city_grouped['percent_change'], 'o', color='#0035a0', label='Original Data', zorder=1)
ax.plot(dates_smooth, smooth_line, linewidth=3.0, color='#0035a0', label='Smoothened Line', zorder=2, solid_capstyle='round')
ax.set_ylim(-100, 100)
ax.axhline(y=0, color='gray', zorder=1, linewidth=.8)
ax.set_title(city_name + " - population change trends")
ax.xaxis.set_tick_params(rotation=0)
ax.yaxis.set_major_formatter('{x:1.0f}%')
ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)
ax.yaxis.set_ticks_position('none')
ax.yaxis.set_major_locator(ticker.MultipleLocator(25))
myFmt = DateFormatter("%d %b")
ax.xaxis.set_major_formatter(myFmt)
ax.patch.set_alpha(0)
ax.fill_between(dates_smooth, smooth_line, where=smooth_line>0, interpolate=True, color='#6ec5bc', alpha=.1, zorder=-2)
ax.fill_between(dates_smooth, smooth_line, where=smooth_line<0, interpolate=True, color='#ed6b4d', alpha=.1, zorder=-2)
ax.annotate(f'{city_grouped['percent_change'][-1]:.0f}%', (city_grouped['date'][-1], city_grouped['percent_change'][-1]), textcoords="offset points", xytext=(0,10), ha='center')
plt.savefig(f'outputs/{city_name}.svg', format="svg", bbox_inches='tight', transparent=True)

city_name = 'Petit Martinique'
petitmartinique = ["03230322010112"]
city = df.filter(pl.col('quadkey').is_in(petitmartinique))

city_grouped = (
    city
    .group_by(['date'])
    .agg([
        pl.sum('mean_n_baseline').alias('baseline'),
        pl.sum('mean_n_crisis').alias('crisis')
    ]).with_columns([
            ((pl.col('crisis')-pl.col('baseline'))*100/pl.col('baseline')).round(0).alias('percent_change'),
        ])
).sort(by ='date')

dates = mpl.dates.date2num(city_grouped['date'].to_list())
cs = CubicSpline(dates, city_grouped['percent_change'].to_list())
dates_new = np.linspace(dates.min(), dates.max(), 300)
smooth_line = cs(dates_new)
dates_smooth = mpl.dates.num2date(dates_new)

fig, ax = plt.subplots(figsize=(5,3), tight_layout=True)
ax.plot(city_grouped['date'], city_grouped['percent_change'], 'o', color='#0035a0', label='Original Data', zorder=1)
ax.plot(dates_smooth, smooth_line, linewidth=3.0, color='#0035a0', label='Smoothened Line', zorder=2, solid_capstyle='round')
ax.set_ylim(-75, 75)
ax.axhline(y=0, color='gray', zorder=1, linewidth=.8)
ax.set_title(city_name + " - population change trends")
ax.xaxis.set_tick_params(rotation=0)
ax.yaxis.set_major_formatter('{x:1.0f}%')
ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)
ax.yaxis.set_ticks_position('none')
ax.yaxis.set_major_locator(ticker.MultipleLocator(25))
myFmt = DateFormatter("%d %b")
ax.xaxis.set_major_formatter(myFmt)
ax.patch.set_alpha(0)
#ax.set_xlim(left=matplotlib.dates.date2num(city_grouped['date'].to_list()))
ax.fill_between(dates_smooth, smooth_line, where=smooth_line>0, interpolate=True, color='#6ec5bc', alpha=.1, zorder=-2)
ax.fill_between(dates_smooth, smooth_line, where=smooth_line<0, interpolate=True, color='#ed6b4d', alpha=.1, zorder=-2)
ax.annotate(f'{city_grouped['percent_change'][-1]:.0f}%', (city_grouped['date'][-1], city_grouped['percent_change'][-1]), textcoords="offset points", xytext=(0,10), ha='center')
plt.savefig(f'outputs/{city_name}.svg', format="svg", bbox_inches='tight', transparent=True)


city_name = 'Grenville'
grenville = ["03230322021211", "03230322021033", "03230322021122"]
city = df.filter(pl.col('quadkey').is_in(grenville))

city_grouped = (
    city
    .group_by(['date'])
    .agg([
        pl.sum('mean_n_baseline').alias('baseline'),
        pl.sum('mean_n_crisis').alias('crisis')
    ]).with_columns([
            ((pl.col('crisis')-pl.col('baseline'))*100/pl.col('baseline')).round(0).alias('percent_change'),
        ])
).sort(by ='date')

dates = mpl.dates.date2num(city_grouped['date'].to_list())
cs = CubicSpline(dates, city_grouped['percent_change'].to_list())
dates_new = np.linspace(dates.min(), dates.max(), 300)
smooth_line = cs(dates_new)
dates_smooth = mpl.dates.num2date(dates_new)


fig, ax = plt.subplots(figsize=(5,3), tight_layout=True)
ax.plot(city_grouped['date'], city_grouped['percent_change'], 'o', color='#0035a0', label='Original Data', zorder=1)
ax.plot(dates_smooth, smooth_line, linewidth=3.0, color='#0035a0', label='Smoothened Line', zorder=2, solid_capstyle='round')
ax.set_ylim(-75, 75)
ax.axhline(y=0, color='gray', zorder=1, linewidth=.8)
ax.set_title(city_name + " - population change trends")
ax.xaxis.set_tick_params(rotation=0)
ax.yaxis.set_major_formatter('{x:1.0f}%')
ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)
ax.yaxis.set_ticks_position('none')
ax.yaxis.set_major_locator(ticker.MultipleLocator(25))
myFmt = DateFormatter("%d %b")
ax.xaxis.set_major_formatter(myFmt)
ax.patch.set_alpha(0)
ax.fill_between(dates_smooth, smooth_line, where=smooth_line>0, interpolate=True, color='#6ec5bc', alpha=.1, zorder=-2)
ax.fill_between(dates_smooth, smooth_line, where=smooth_line<0, interpolate=True, color='#ed6b4d', alpha=.1, zorder=-2)
ax.annotate(f'{city_grouped['percent_change'][-1]:.0f}%', (city_grouped['date'][-1], city_grouped['percent_change'][-1]), textcoords="offset points", xytext=(0,10), ha='center')
plt.savefig(f'outputs/{city_name}.svg', format="svg", bbox_inches='tight', transparent=True)


## jamaica
city_name = 'Savanna-la-mer'
savanna = ["03221020231211", "03221020231300", "03221020231033","03221020231122"]
city = df.filter(pl.col('quadkey').is_in(savanna))

city_grouped = (
    city
    .group_by(['date'])
    .agg([
        pl.sum('mean_n_baseline').alias('baseline'),
        pl.sum('mean_n_crisis').alias('crisis')
    ]).with_columns([
            ((pl.col('crisis')-pl.col('baseline'))*100/pl.col('baseline')).round(0).alias('percent_change'),
        ])
).sort(by ='date')

dates = mpl.dates.date2num(city_grouped['date'].to_list())
cs = CubicSpline(dates, city_grouped['percent_change'].to_list())
dates_new = np.linspace(dates.min(), dates.max(), 300)
smooth_line = cs(dates_new)
dates_smooth = mpl.dates.num2date(dates_new)

fig, ax = plt.subplots(figsize=(5,3), tight_layout=True)
ax.plot(city_grouped['date'], city_grouped['percent_change'], 'o', color='#0035a0', label='Original Data', zorder=1)
ax.plot(dates_smooth, smooth_line, linewidth=3.0, color='#0035a0', label='Smoothened Line', zorder=2, solid_capstyle='round')
ax.set_ylim(-90, 90)
ax.axhline(y=0, color='gray', zorder=1, linewidth=.8)
ax.set_title(city_name + " - population change trends")
ax.xaxis.set_tick_params(rotation=0)
ax.yaxis.set_major_formatter('{x:1.0f}%')
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)
ax.yaxis.set_ticks_position('none')
ax.yaxis.set_major_locator(ticker.MultipleLocator(25))
myFmt = DateFormatter("%d %b")
ax.xaxis.set_major_formatter(myFmt)
ax.patch.set_alpha(0)
ax.fill_between(dates_smooth, smooth_line, where=smooth_line>0, interpolate=True, color='#6ec5bc', alpha=.1, zorder=-2)
ax.fill_between(dates_smooth, smooth_line, where=smooth_line<0, interpolate=True, color='#ed6b4d', alpha=.1, zorder=-2)
ax.annotate(f'{city_grouped['percent_change'][-1]:.0f}%', (city_grouped['date'][-1], city_grouped['percent_change'][-1]), textcoords="offset points", xytext=(0,10), ha='center')
ax.annotate(f'{city_grouped['percent_change'][-1]:.0f}%', (city_grouped['date'][-1], city_grouped['percent_change'][-1]), textcoords="offset points", xytext=(0,10), ha='center')
plt.savefig(f'outputs/{city_name}.svg', format="svg", bbox_inches='tight', transparent=True)

city_name = 'Old Harbour'
old_harbour = ["03221023001030", "03221023001012", "03221023001013","03221023001031"]
city = df.filter(pl.col('quadkey').is_in(old_harbour))

city_grouped = (
    city
    .group_by(['date'])
    .agg([
        pl.sum('mean_n_baseline').alias('baseline'),
        pl.sum('mean_n_crisis').alias('crisis')
    ]).with_columns([
            ((pl.col('crisis')-pl.col('baseline'))*100/pl.col('baseline')).round(0).alias('percent_change'),
        ])
).sort(by ='date')

dates = mpl.dates.date2num(city_grouped['date'].to_list())
cs = CubicSpline(dates, city_grouped['percent_change'].to_list())
dates_new = np.linspace(dates.min(), dates.max(), 300)
smooth_line = cs(dates_new)
dates_smooth = mpl.dates.num2date(dates_new)

fig, ax = plt.subplots(figsize=(5,3), tight_layout=True)
ax.plot(city_grouped['date'], city_grouped['percent_change'], 'o', color='#0035a0', label='Original Data', zorder=1)
ax.plot(dates_smooth, smooth_line, linewidth=3.0, color='#0035a0', label='Smoothened Line', zorder=2, solid_capstyle='round')
ax.set_ylim(-80, 80)
ax.axhline(y=0, color='gray', zorder=1, linewidth=.8)
ax.set_title(city_name + " - population change trends")
ax.xaxis.set_tick_params(rotation=0)
ax.yaxis.set_major_formatter('{x:1.0f}%')
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)
ax.yaxis.set_ticks_position('none')
ax.yaxis.set_major_locator(ticker.MultipleLocator(25))
myFmt = DateFormatter("%d %b")
ax.xaxis.set_major_formatter(myFmt)
ax.patch.set_alpha(0)
ax.fill_between(dates_smooth, smooth_line, where=smooth_line>0, interpolate=True, color='#6ec5bc', alpha=.1, zorder=-2)
ax.fill_between(dates_smooth, smooth_line, where=smooth_line<0, interpolate=True, color='#ed6b4d', alpha=.1, zorder=-2)
ax.annotate(f'{city_grouped['percent_change'][-1]:.0f}%', (city_grouped['date'][-1], city_grouped['percent_change'][-1]), textcoords="offset points", xytext=(0,10), ha='center')
plt.savefig(f'outputs/{city_name}.svg', format="svg", bbox_inches='tight', transparent=True)

## jamaica end

city_name = 'St. George\'s'
stgeorges = ["03230322020323"]
city = df.filter(pl.col('quadkey').is_in(stgeorges))

city_grouped = (
    city
    .group_by(['date'])
    .agg([
        pl.sum('mean_n_baseline').alias('baseline'),
        pl.sum('mean_n_crisis').alias('crisis')
    ]).with_columns([
            ((pl.col('crisis')-pl.col('baseline'))*100/pl.col('baseline')).round(0).alias('percent_change'),
        ])
).sort(by ='date')

dates = mpl.dates.date2num(city_grouped['date'].to_list())
cs = CubicSpline(dates, city_grouped['percent_change'].to_list())
dates_new = np.linspace(dates.min(), dates.max(), 300)
smooth_line = cs(dates_new)
dates_smooth = mpl.dates.num2date(dates_new)

fig, ax = plt.subplots(figsize=(5,3), tight_layout=True)
ax.plot(city_grouped['date'], city_grouped['percent_change'], 'o', color='#0035a0', label='Original Data', zorder=1)
ax.plot(dates_smooth, smooth_line, linewidth=3.0, color='#0035a0', label='Smoothened Line', zorder=2, solid_capstyle='round')
ax.set_ylim(-60, 60)
ax.axhline(y=0, color='gray', zorder=1, linewidth=.8)
ax.set_title(city_name + " - population change trends")
ax.xaxis.set_tick_params(rotation=0)
ax.yaxis.set_major_formatter('{x:1.0f}%')
ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)
ax.yaxis.set_ticks_position('none')
ax.yaxis.set_major_locator(ticker.MultipleLocator(25))
myFmt = DateFormatter("%d %b")
ax.xaxis.set_major_formatter(myFmt)
ax.patch.set_alpha(0)
#ax.set_xlim(left=matplotlib.dates.date2num(city_grouped['date'].to_list()))
ax.fill_between(dates_smooth, smooth_line, where=smooth_line>0, interpolate=True, color='#6ec5bc', alpha=.1, zorder=-2)
ax.fill_between(dates_smooth, smooth_line, where=smooth_line<0, interpolate=True, color='#ed6b4d', alpha=.1, zorder=-2)
ax.annotate(f'{city_grouped['percent_change'][-1]:.0f}%', (city_grouped['date'][-1], city_grouped['percent_change'][-1]), textcoords="offset points", xytext=(0,10), ha='center')
plt.savefig(f'outputs/{city_name}.svg', format="svg", bbox_inches='tight', transparent=True)

city_name = 'Clifton'
clifton = ["03230320232320"]
city = df.filter(pl.col('quadkey').is_in(clifton))

city_grouped = (
    city
    .group_by(['date'])
    .agg([
        pl.sum('mean_n_baseline').alias('baseline'),
        pl.sum('mean_n_crisis').alias('crisis')
    ]).with_columns([
            ((pl.col('crisis')-pl.col('baseline'))*100/pl.col('baseline')).round(0).alias('percent_change'),
        ])
).sort(by ='date')

dates = mpl.dates.date2num(city_grouped['date'].to_list())
cs = CubicSpline(dates, city_grouped['percent_change'].to_list())
dates_new = np.linspace(dates.min(), dates.max(), 300)
smooth_line = cs(dates_new)
dates_smooth = mpl.dates.num2date(dates_new)

fig, ax = plt.subplots(figsize=(5,3), tight_layout=True)
ax.plot(city_grouped['date'], city_grouped['percent_change'], 'o', color='#0035a0', label='Original Data', zorder=1)
ax.plot(dates_smooth, smooth_line, linewidth=3.0, color='#0035a0', label='Smoothened Line', zorder=2, solid_capstyle='round')
ax.set_ylim(-80, 80)
ax.axhline(y=0, color='gray', zorder=1, linewidth=.8)
ax.set_title(city_name + " - population change trends")
ax.xaxis.set_tick_params(rotation=0)
ax.yaxis.set_major_formatter('{x:1.0f}%')
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)
ax.yaxis.set_ticks_position('none')
ax.yaxis.set_major_locator(ticker.MultipleLocator(25))
myFmt = DateFormatter("%d %b")
ax.xaxis.set_major_formatter(myFmt)
ax.patch.set_alpha(0)
#ax.set_xlim(left=matplotlib.dates.date2num(city_grouped['date'].to_list()))
ax.fill_between(dates_smooth, smooth_line, where=smooth_line>0, interpolate=True, color='#6ec5bc', alpha=.1, zorder=-2)
ax.fill_between(dates_smooth, smooth_line, where=smooth_line<0, interpolate=True, color='#ed6b4d', alpha=.1, zorder=-2)
ax.annotate(f'{city_grouped['percent_change'][-1]:.0f}%', (city_grouped['date'][-1], city_grouped['percent_change'][-1]), textcoords="offset points", xytext=(0,10), ha='center')
plt.savefig(f'outputs/{city_name}.svg', format="svg", bbox_inches='tight', transparent=True)

city_name = 'Mayreau'
mayreau = ["03230320232301"]
city = df.filter(pl.col('quadkey').is_in(mayreau))

city_grouped = (
    city
    .group_by(['date'])
    .agg([
        pl.sum('mean_n_baseline').alias('baseline'),
        pl.sum('mean_n_crisis').alias('crisis')
    ]).with_columns([
            ((pl.col('crisis')-pl.col('baseline'))*100/pl.col('baseline')).round(0).alias('percent_change'),
        ])
).sort(by ='date')

dates = mpl.dates.date2num(city_grouped['date'].to_list())
cs = CubicSpline(dates, city_grouped['percent_change'].to_list())
dates_new = np.linspace(dates.min(), dates.max(), 300)
smooth_line = cs(dates_new)
dates_smooth = mpl.dates.num2date(dates_new)


fig, ax = plt.subplots(figsize=(5,3), tight_layout=True)
ax.plot(city_grouped['date'], city_grouped['percent_change'], 'o', color='#0035a0', label='Original Data', zorder=1)
ax.plot(dates_smooth, smooth_line, linewidth=3.0, color='#0035a0', label='Smoothened Line', zorder=2, solid_capstyle='round')
ax.set_ylim(-60, 60)
ax.axhline(y=0, color='gray', zorder=1, linewidth=.8)
ax.set_title(city_name + " - population change trends")
ax.xaxis.set_tick_params(rotation=0)
ax.yaxis.set_major_formatter('{x:1.0f}%')
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)
ax.yaxis.set_ticks_position('none')
ax.yaxis.set_major_locator(ticker.MultipleLocator(25))
myFmt = DateFormatter("%d %b")
ax.xaxis.set_major_formatter(myFmt)
ax.patch.set_alpha(0)
#ax.set_xlim(left=matplotlib.dates.date2num(city_grouped['date'].to_list()))
ax.fill_between(dates_smooth, smooth_line, where=smooth_line>0, interpolate=True, color='#6ec5bc', alpha=.1, zorder=-2)
ax.fill_between(dates_smooth, smooth_line, where=smooth_line<0, interpolate=True, color='#ed6b4d', alpha=.1, zorder=-2)
ax.annotate(f'{city_grouped['percent_change'][-1]:.0f}%', (city_grouped['date'][-1], city_grouped['percent_change'][-1]), textcoords="offset points", xytext=(0,10), ha='center')
plt.savefig(f'outputs/{city_name}.svg', format="svg", bbox_inches='tight', transparent=True)

# building damage map
filepath = 'input/damaged.geojson'
gdf = gpd.read_file(filepath, engine="pyogrio", use_arrow=True)

# Keep columns necessary for our visualization
#cols = ["shapeName", "shapeID", "geometry"]
#gdf = gdf[cols]
layer = SolidPolygonLayer.from_geopandas(gdf, get_fill_color=[210, 38, 48])
map = Map(layers=[layer], view_state={"longitude": -61.455116, "latitude": 12.479822, "zoom": 14})
map.to_html("outputs/building_damage.html")