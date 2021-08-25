available_frequencies = {
    'B':'business day frequency',
    'C':'custom business day frequency',
    'D':'calendar day frequency',
    'W':'weekly frequency',
    'M':'month end frequency',
    'SM':'semi-month end frequency (15th and end of month)',
    'BM':'business month end frequency',
    'CBM':'custom business month end frequency',
    'MS':'month start frequency',
    'SMS':'semi-month start frequency (1st and 15th)',
    'BMS':'business month start frequency',
    'CBMS':'custom business month start frequency',
    'Q':'quarter end frequency',
    'BQ':'business quarter end frequency',
    'QS':'quarter start frequency',
    'BQS':'business quarter start frequency',
    'A, Y ':'year end frequency',
    'BA, BY':'business year end frequency',
    'AS, YS':'year start frequency',
    'BAS, BYS':'business year start frequency',
    'BH':'business hour frequency',
    'H':'hourly frequency',
    'min':'minutely frequency',
    'S':'secondly frequency',
    'L, ms':'milliseconds',
    'U, us':'microseconds',
    'N':'nanoseconds',
}


indicators = [
    {'label': 'Close', 
    'value':'close'},
    {'label': 'Scaled Close',
    'value':'scaled_close'},    
    # {'label': 'Rebase',
    # 'value':'rebase'},
    {'label': 'Volume',
    'value':'volume'},
    {'label': '30 Day SMA - Close',
    'value':'sma_30_close'},
    {'label': '60 Day SMA - Close',
    'value':'sma_60_close'},
    {'label': '90 Day SMA - Close',
    'value':'sma_90_close'},
    {'label': '30 Day SMA - Scaled Close',
    'value':'sma_30_scaled_close'},
    {'label': '60 Day SMA - Scaled Close',
    'value':'sma_60_scaled_close'},
    {'label': '90 Day SMA - Scaled Close',
    'value':'sma_90_scaled_close'},
]

INTERVAL_S = {
    "1m": 60,
    "5m": 60 * 5,
    "15m": 60 * 15,
    "30m": 60 * 30,
    "1h": 60 * 60,
    "4h": 60 * 60 * 4,
    "6h": 60 * 60 * 6,
    "12h": 60 * 60 * 12,
    "1d": 60 * 60 * 24,
}

INTERVAL_MS = {
    "1m": INTERVAL_S["1m"] * 1000,
    "5m": INTERVAL_S["5m"] * 1000,
    "15m": INTERVAL_S["15m"] * 1000,
    "30m": INTERVAL_S["30m"] * 1000,
    "1h": INTERVAL_S["1h"] * 1000,
    "4h": INTERVAL_S["4h"] * 1000,
    "6h": INTERVAL_S["6h"] * 1000,
    "12h": INTERVAL_S["12h"] * 1000,
    "1d": INTERVAL_S["1d"] * 1000,
}

INTERVAL_DATA = {
    "1m": {
        "unit": "minute",
        "frequency": 1
    },
    "5m": {
        "unit": "minute",
        "frequency": 5
    },
    "15m": {
        "unit": "minute",
        "frequency": 15
    },
    "30m": {
        "unit": "minute",
        "frequency": 30
    },
    "1h": {
        "unit": "hour",
        "frequency": 1
    },
    "4h": {
        "unit": "hour",
        "frequency": 4
    },
    "6h": {
        "unit": "hour",
        "frequency": 6
    },
    "12h": {
        "unit": "hour",
        "frequency": 12
    },
    "1d": {
        "unit": "day",
        "frequency": 1
    }
}