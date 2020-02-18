import numpy as np


def pad(data, pad_value=1):
    data_padded = data
    for i in range(pad_value-1):
        data_padded = np.concatenate((data_padded, data))
    return data_padded


def unpad(padded_data, pad_value=1):
    lim = int(len(padded_data)/pad_value)
    data = padded_data[0:lim]
    return data

