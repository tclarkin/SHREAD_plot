# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import hydroimport as hydro

from database import SBSP_iv, SBSP_dv, SASP_iv, SASP_dv
from database import csas_gages, dust_ts, dust_layers


def get_csas_plot(start_date, end_date, plot_dust, csas_sel, dtype,plot_albedo):
    """
    :description: this function updates the snowplot
    :param start_date: start date (from date selector)
    :param end_date: end date (from date selector)
    :param plot_dust: boolean for plotting dust layers
    :param csas_sel: list of selected csas sites ([])
    :param dtype: data type (dv/iv)
    :return: update figure
    """
    # Create date axis
    dates = pd.date_range(start_date, end_date, freq="D", tz='UTC')
    # Set snow type based on user selection
    cvar = "Sno_Height_M"

    ## Process CSAS data (if selected)
    if len(csas_sel)>0:
        for sp in ["PTSP","SBSG"]:
            if sp in csas_sel:
                csas_sel.remove(sp)

    if dtype=="iv":
        cdates = pd.date_range(start_date, end_date, freq="H", tz='UTC')
    else:
        cdates = dates

    csas_s_df = pd.DataFrame(index=cdates)
    if plot_albedo==True:
        csas_a_df = pd.DataFrame(index=cdates)

    for c in csas_sel:
        print(c)
        if c=="SASP":
            if dtype=="dv":
                csas_in = SASP_dv
            if dtype=="iv":
                csas_in = SASP_iv
        if c=="SBSP":
            if dtype=="dv":
                csas_in = SBSP_dv
            if dtype=="iv":
                csas_in = SBSP_iv

        csas_in = csas_in[(csas_in.index>=start_date) & (csas_in.index<=end_date)]
        csas_in = csas_s_df.merge(csas_in, left_index=True, right_index=True, how="left")
        csas_s_df.loc[:, c] = csas_in[cvar]*3.28*12

        if plot_albedo == True:
            csas_a_df.loc[:, c] = csas_in["PyDwn_Unfilt_W"] / csas_in["PyUp_Unfilt_W"]
            csas_a_df.loc[csas_a_df[c] > 1, c] = 1
            csas_a_df.loc[csas_a_df[c] < 0, c] = 0

    if plot_albedo == True:
        csas_a_df = (1 - csas_a_df) * 100

    if len(csas_sel) == 0:
        csas_max = np.nan
        print("No CSAS selected.")
    else:
        csas_max = csas_s_df.max().max()

    ### Plot the data
    ymax = max([csas_max,20]) * 1.25

    print("Updating csas plot...")
    fig = go.Figure()

    for c in csas_sel:
        fig.add_trace(go.Scatter(
            x=csas_s_df.index,
            y=csas_s_df[c],
            text="Snow Depth (in)",
            mode='lines',
            line=dict(color=csas_gages.loc[c, "color"],dash="dot"),
            name=c))

    if plot_dust == True:
        for d in dust_ts.columns:
            fig.add_trace(go.Scatter(
                x=dust_ts.index,
                y=dust_ts[d],
                text="Dust Layer Height (in)",
                mode='lines+markers',
                line=dict(color=dust_layers.loc[d, "color"],dash="dot"),
                name=d))

    if plot_albedo == True:
        for c in csas_a_df.columns:
            fig.add_trace(go.Scatter(
                x=csas_a_df.index,
                y=csas_a_df[c],
                text="100% - Albedo",
                mode='lines',
                line=dict(color=csas_gages.loc[c, "color"],dash="dash"),
                name=c+" 100% - Albedo",
                yaxis="y2"))

    fig.update_layout(
        margin={'l': 40, 'b': 40, 't': 0, 'r': 45},
        height=400,
        legend={'x': 0, 'y': 1, 'bgcolor': 'rgba(255,255,255,0.8)'},
        hovermode='closest',
        plot_bgcolor='white',
        xaxis=dict(
            range=[start_date, end_date],
            showline=True,
            linecolor="black",
            mirror=True
        ),
        yaxis=dict(
            title='Depth (in)',
            side="left",
            range=[0, ymax],
            showline=True,
            linecolor="black",
            mirror=True
        ))

    if plot_albedo == True:
        fig.update_layout(
            yaxis2=dict(
            title="100% - Albedo",
            side="right",
            overlaying='y',
            range=[0,100]),
            margin = {'l': 40, 'b': 40, 't': 0, 'r': 40},
        )
    print('csas plot is done')
    
    return fig