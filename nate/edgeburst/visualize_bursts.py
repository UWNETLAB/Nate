"""
This is a MODULE docstring
"""

import nate
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def to_pandas(ebursts, offsets, unit='s'):
    """
    TODO: write docstring

    ebursts is an edgebust dict from the SVO object
    offsets is an offsets dict from the SVO object
    """
    bdf = pd.DataFrame(ebursts)
    bdf[1] = pd.to_datetime(bdf[1], unit=unit)
    bdf[2] = pd.to_datetime(bdf[2], unit=unit)
    bdf.columns = ['level', 'start', 'end']

    odf = pd.DataFrame()
    i = pd.to_datetime(offsets, unit='s')
    odf['Date'], odf['Year'], odf['Month'], odf['Day'] = i.date, i.year, i.month, i.day
    odf = odf.set_index(i)

    return bdf, odf


def plot_bursts(odf, bdf, lowest_level=0, daterange=None, xrangeoffsets=3):
    """
    TODO: write docstring

    odf = an offsets dataframe 
    bdf = an edgeburst dataframe
    lowest_level = subset the burst dataframe with bursts greater than or equal to the specified level
    daterange = a tuple with two elements: a start date and end date as *strings*. format is 'year-month-day'
    xrangeoffsets = the number of days to add before and after the min and max x dates
    """
    if lowest_level > 0:
        bdf = bdf[bdf['level'] >= lowest_level]
        xmin = (min(bdf['start']) + pd.DateOffset(days=2)).date()
        xmax = (max(bdf['start']) + pd.DateOffset(days=2)).date()
        daterange = (xmin, xmax)

    fig, (axa, axb) = plt.subplots(2, sharey=False, sharex=True)
    fig.set_figwidth(10)
    fig.set_figheight(6)

    formatter = mdates.DateFormatter("%b %d\n%Y")
    axb.xaxis.set_major_formatter(formatter)

    # offsets plot
    day_freq = odf.resample('D').size()
    axa.plot(day_freq, color='#32363A')
    axa.xaxis.set_major_formatter(formatter)
    axa.xaxis_date()
    axa.tick_params(axis='both', which='both', length=0)
    axa.set_ylabel('Daily offsets')
    if daterange:
        axa.set_xlim(pd.Timestamp(daterange[0]), pd.Timestamp(daterange[1]))

    # bursts plot
    axb.bar(bdf['start'], bdf['level'], color='#32363A')
    axb.set_ylabel('Burst level')
    axb.tick_params(axis='both', which='both', length=0)
    if daterange:
        axb.set_xlim(pd.Timestamp(daterange[0]), pd.Timestamp(daterange[1]))
