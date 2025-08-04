def is_heikin_ashi_doji(ha_row, threshold=0.1):
    body = abs(ha_row['HA_Open'] - ha_row['HA_Close'])
    rng = ha_row['HA_High'] - ha_row['HA_Low']
    return rng > 0 and (body / rng) < threshold