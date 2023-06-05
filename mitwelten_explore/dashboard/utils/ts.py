import numpy as np
from scipy.stats import pearsonr
from scipy.signal import find_peaks, find_peaks_cwt
from datetime import datetime
import time

def check_array_len(arrays):
    for arr in arrays:
        if len(arr)<2:
            return False
    return True

def interpolate_nan(a:list):
    if not isinstance(a, np.ndarray):
        a = np.array(a)
    xi = np.arange(len(a))

    mask = np.isfinite(a)
    a_interp = np.interp(xi, xi[mask], a[mask])
    return list(a_interp)

def correlation_matrix(data:list):
    #t0 = time.time()
    # data: [[[]]]
    # data[0] : [[time string list],[values_list]]
    if len(data) <2:
        return None
    num_datasets = len(data)
    
    values_list = []
    timestamps_list = []
    for i in range(len(data)):
        timestamps_list.append([datetime.fromisoformat(d) for d in data[i][0]])
        values_list.append(data[i][1])
    timestamps_unix_list = []
    for timestamps in timestamps_list:
        timestamps_unix_list.append(np.array([dt.timestamp() for dt in timestamps]))
    correlation_matrix = np.zeros((num_datasets, num_datasets))

    for i in range(num_datasets):
        for j in range(i+1, num_datasets):
            if check_array_len([timestamps_unix_list[i], timestamps_unix_list[j], values_list[j], values_list[i]]):
                interpolated_values_j = np.interp(timestamps_unix_list[i], timestamps_unix_list[j], values_list[j])
                correlation, _ = pearsonr(values_list[i], interpolated_values_j)
                correlation_matrix[i, j] = correlation
            else: 
                correlation_matrix[i, j] = None

            
    #print(correlation_matrix)
    #print("took",time.time()-t0)
    return correlation_matrix

def compute_fft(amplitude, times):
    t0 = time.time()
    if isinstance(times[0], str):
        times = [datetime.fromisoformat(d) for d in times]
    amplitude = interpolate_nan(amplitude)
    n = len(amplitude)
    n = n-(n%24)
    ft = np.fft.fft(amplitude, n=n) / n
    ft = ft[range(int(n/ 2))]


    values = np.arange(int(n / 2))
    tp = n * ((times[1]-times[0]).seconds)
    frequencies = values / tp
    periods_s = [round(1/f) for f in frequencies[1:]]
    aft = list(np.abs(ft))
    print("took",time.time()-t0)

    return aft[1:],periods_s

def create_fft_bins(aft,time_periods_s,n_bins=256, agg_fcn = np.max):
    minf = min(time_periods_s)
    maxf=max(time_periods_s)
    lgs = np.logspace(np.log10(maxf),np.log10(minf), n_bins, endpoint=True)
    dig = np.digitize(time_periods_s, lgs)
    aggregated_values = []
    bucket_ends = []
    for i in range(len(lgs)):
        indicies = list(np.where(dig==i)[0])
        if len(indicies)>0:
            bucket_val = agg_fcn([aft[i] for i in indicies])
            aggregated_values.append(bucket_val)
            bucket_ends.append(lgs[i])
    return aggregated_values,bucket_ends