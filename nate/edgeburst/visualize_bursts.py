"""
This is a MODULE docstring
"""

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def to_pandas(ebursts, offsets, svo, unit='s'):
    """
    TODO: write docstring

    ebursts is an edgebust dict from the SVO object
    offsets is an offsets dict from the SVO object
    """
    svos = " | ".join(svo)

    bdf = pd.DataFrame(ebursts)
    bdf[1] = pd.to_datetime(bdf[1], unit=unit)
    bdf[2] = pd.to_datetime(bdf[2], unit=unit)
    bdf.columns = ['level', 'start', 'end']
    bdf['svo'] = svos

    odf = pd.DataFrame()
    i = pd.to_datetime(offsets, unit='s')
    odf['Date'], odf['Year'], odf['Month'], odf[
        'Day'] = i.date, i.year, i.month, i.day
    odf = odf.set_index(i)
    odf['svo'] = svos

    return bdf, odf


def plot_bursts(odf,
                bdf,
                lowest_level=0,
                title=True,
                daterange=None,
                xrangeoffsets=3,
                s=None,
                gamma=None):
    """
    TODO: write docstring

    odf = an offsets dataframe 
    bdf = an edgeburst dataframe
    lowest_level = subset the burst dataframe with bursts greater than or equal to the specified level
    daterange = a tuple with two elements: a start date and end date as *strings*. format is 'year-month-day'
    xrangeoffsets = the number of days to add before and after the min and max x dates
    """

    svo_title = str(set(bdf['svo']).pop())

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

    if s != None and gamma != None:
        axb.set_ylabel(r'Burst levels (s = {}, $\gamma$ = {})'.format(
            s, gamma))
    else:
        axb.set_ylabel('Burst level')

    axb.tick_params(axis='both', which='both', length=0)

    if daterange:
        axb.set_xlim(pd.Timestamp(daterange[0]), pd.Timestamp(daterange[1]))

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    if title is True:
        fig.suptitle(f'SVO: {svo_title}', fontsize=12, ha='center')
