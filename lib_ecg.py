 # Imports
# compat
from __future__ import absolute_import, division, print_function
from six.moves import range, zip

# 3rd party
import math
import numpy as np
import scipy.signal as ss
import matplotlib.pyplot as plt
from scipy import stats, integrate

# local
from . import tools as st
from .. import plotting, utils
from biosppy.inter_plotting import ecg as inter_plotting
from scipy.signal import argrelextrema


def ecg(signal=None, sampling_rate=1000.0, path=None, show=True, interactive=False):
    """Process a raw ECG signal and extract relevant signal features using
    default parameters.

    Parameters
    ----------
    signal : array
        Raw ECG signal.
    sampling_rate : int, float, optional
        Sampling frequency (Hz).
    path : str, optional
        If provided, the plot will be saved to the specified file.
    show : bool, optional
        If True, show a summary plot.
    interactive : bool, optional
        If True, shows an interactive plot.

    Returns
    -------
    ts : array
        Signal time axis reference (seconds).
    filtered : array
        Filtered ECG signal.
    rpeaks : array
        R-peak location indices.
    templates_ts : array
        Templates time axis reference (seconds).
    templates : array
        Extracted heartbeat templates.
    heart_rate_ts : array
        Heart rate time axis reference (seconds).
    heart_rate : array
        Instantaneous heart rate (bpm).

    """

    # check inputs
    if signal is None:
        raise TypeError("Please specify an input signal.")

    # ensure numpy
    signal = np.array(signal)

    sampling_rate = float(sampling_rate)

    # filter signal
    order = int(0.3 * sampling_rate)
    filtered, _, _ = st.filter_signal(
        signal=signal,
        ftype="FIR",
        band="bandpass",
        order=order,
        frequency=[3, 45],
        sampling_rate=sampling_rate,
    )

    # segment
    (rpeaks,) = hamilton_segmenter(signal=filtered, sampling_rate=sampling_rate)

    # correct R-peak locations
    (rpeaks,) = correct_rpeaks(
        signal=filtered, rpeaks=rpeaks, sampling_rate=sampling_rate, tol=0.05
    )

    # extract templates
    templates, rpeaks = extract_heartbeats(
        signal=filtered,
        rpeaks=rpeaks,
        sampling_rate=sampling_rate,
        before=0.2,
        after=0.4,
    )

    # compute heart rate
    hr_idx, hr = st.get_heart_rate(
        beats=rpeaks, sampling_rate=sampling_rate, smooth=True, size=3
    )

    # get time vectors
    length = len(signal)
    T = (length - 1) / sampling_rate
    ts = np.linspace(0, T, length, endpoint=True)
    ts_hr = ts[hr_idx]
    ts_tmpl = np.linspace(-0.2, 0.4, templates.shape[1], endpoint=False)

    # plot
    if show:
        if interactive:
            inter_plotting.plot_ecg(
                ts=ts,
                raw=signal,
                filtered=filtered,
                rpeaks=rpeaks,
                templates_ts=ts_tmpl,
                templates=templates,
                heart_rate_ts=ts_hr,
                heart_rate=hr,
                path=path,
                show=True,
            )
            print(filtered)

        else:
            plotting.plot_ecg(
                ts=ts,
                raw=signal,
                filtered=filtered,
                rpeaks=rpeaks,
                templates_ts=ts_tmpl,
                templates=templates,
                heart_rate_ts=ts_hr,
                heart_rate=hr,
                path=path,
                show=True,
            )

    # output
    args = (ts, filtered, rpeaks, ts_tmpl, templates, ts_hr, hr)
    names = (
        "ts",
        "filtered",
        "rpeaks",
        "templates_ts",
        "templates",
        "heart_rate_ts",
        "heart_rate",
    )

    return utils.ReturnTuple(args, names)
