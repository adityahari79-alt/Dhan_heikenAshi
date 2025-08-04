import pandas as pd

def heikin_ashi(df):
    df_HA = df.copy()
    df_HA['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    ha_open = [(df['Open'][0] + df['Close'][0]) / 2]
    for i in range(1, len(df)):
        ha_open.append((ha_open[i-1] + df_HA['HA_Close'][i-1]) / 2)
    df_HA['HA_Open'] = ha_open
    df_HA['HA_High'] = df[['High', 'Open', 'Close']].max(axis=1)
    df_HA['HA_Low'] = df[['Low', 'Open', 'Close']].min(axis=1)
    return df_HA