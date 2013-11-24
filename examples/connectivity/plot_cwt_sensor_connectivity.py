"""
==============================================================
Compute seed based time-frequency connectivity in sensor space
==============================================================

Computes the connectivity between a seed-gradiometer close to the visual cortex
and all other gradiometers. The connectivity is computed in the time-frequency
domain using Morlet wavelets and the debiased Squared Weighted Phase Lag Index
[1] is used as connectivity metric.

[1] Vinck et al. "An improved index of phase-synchronization for electro-
    physiological data in the presence of volume-conduction, noise and
    sample-size bias" NeuroImage, vol. 55, no. 4, pp. 1548-1565, Apr. 2011.
"""

# Author: Martin Luessi <mluessi@nmr.mgh.harvard.edu>
#
# License: BSD (3-clause)

print __doc__

import numpy as np
import mne
from mne import fiff
from mne.connectivity import spectral_connectivity, seed_target_indices
from mne.datasets import sample
from mne.layouts import read_layout
from mne.viz import plot_topo_tfr

###############################################################################
# Set parameters
data_path = sample.data_path()
raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'
event_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw-eve.fif'

# Setup for reading the raw data
raw = fiff.Raw(raw_fname)
events = mne.read_events(event_fname)

# Add a bad channel
raw.info['bads'] += ['MEG 2443']

# Pick MEG gradiometers
picks = fiff.pick_types(raw.info, meg='grad', eeg=False, stim=False, eog=True,
                        exclude='bads')

# Create epochs for left-visual condition
event_id, tmin, tmax = 3, -0.2, 0.5
epochs = mne.Epochs(raw, events, event_id, tmin, tmax, picks=picks,
                    baseline=(None, 0), reject=dict(grad=4000e-13, eog=150e-6))

# Use 'MEG 2343' as seed
seed_ch = 'MEG 2343'
picks_ch_names = [raw.ch_names[i] for i in picks]

# Create seed-target indices for connectivity computation
seed = picks_ch_names.index(seed_ch)
targets = np.arange(len(picks))
indices = seed_target_indices(seed, targets)

# Define wavelet frequencies and number of cycles
cwt_frequencies = np.arange(7, 30, 2)
cwt_n_cycles = cwt_frequen  cies / 7.

# Run the connectivity analysis using 2 parallel jobs
sfreq = raw.info['sfreq']  # the sampling frequency
con, freqs, times, _, _ = spectral_connectivity(epochs, indices=indices,
    method='wpli2_debiased', mode='cwt_morlet', sfreq=sfreq,
    cwt_frequencies=cwt_frequencies, cwt_n_cycles=cwt_n_cycles, n_jobs=2)

# Mark the seed channel with a value of 1.0, so we can see it in the plot
con[np.where(indices[1] == seed)] = 1.0

# Show topography of connectivity from seed
import matplotlib.pyplot as plt
layout = read_layout('Vectorview-all')
title = 'WPLI2 - Visual - Seed %s' % seed_ch
plot_topo_tfr(epochs, con, freqs, layout, title=title)
plt.show()
