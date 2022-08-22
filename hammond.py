#!/usr/bin/env python
# coding: utf-8

# In[65]:


import os
import numpy as np
from pyo import *

def render(name, params, f, n):
  # In[66]:
  
  params = params.tolist()
  
  
  # In[67]:
  
  
  # --- HAMSYNTH, V1.2 ---
  
  # instantiates and boots server
  # opens audio and MIDI interfaces, sets sample rate and number of channels
  s = Server(buffersize=512, duplex=0, audio="offline").boot()
  s.amp = 0.1 # sets output gain level, -20dB
  
  # --- OSCILLATORS ---
  
  # sets fundamental frequency in Hz
  fund = f
  # sets note duration in seconds
  note_length = n
  
  # frequency multipliers for intervals (excl. fundamental/reference)
  # source: https://pages.mtu.edu/~suits/cents.html
  mul_sub_oct = 0.5
  mul_fifth = 2**(700/1200)
  mul_oct1 = 2
  mul_oct1_fifth = 2**(1900/1200)
  mul_oct2 = 4
  mul_oct2_third = 2**(2800/1200)
  mul_oct2_fifth = 2**(3100/1200)
  mul_oct3 = 8
  
  # SUB-OCTAVE
  
  sub_oct_freq = fund * mul_sub_oct
  sub_oct_phase = 0
  sub_oct_mul = params[0]
  
  sub_oct = Sine(freq=sub_oct_freq, phase=sub_oct_phase, mul=sub_oct_mul)#.out()
  
  # REFERENCE (FUNDAMENTAL)
  
  ref_phase = 0
  ref_mul = params[1]
  
  ref = Sine(freq=fund, phase=ref_phase, mul=ref_mul)#.out()
  
  # FIFTH
  
  fifth_freq = fund * mul_fifth
  fifth_phase = 0
  fifth_mul = params[2]
  
  fifth = Sine(freq=fifth_freq, phase=fifth_phase, mul=fifth_mul)#.out()
  
  # OCTAVE
  
  oct1_freq = fund * mul_oct1
  oct1_phase = 0
  oct1_mul = params[3]
  
  oct1 = Sine(freq=oct1_freq, phase=oct1_phase, mul=oct1_mul)#.out()
  
  # OCTAVE & FIFTH
  
  oct1_fifth_freq = fund * mul_oct1_fifth
  oct1_fifth_phase = 0
  oct1_fifth_mul = params[4]
  
  oct1_fifth = Sine(freq=oct1_fifth_freq, phase=oct1_fifth_phase, mul=oct1_fifth_mul)#.out()
  
  # 2 OCTAVES
  
  oct2_freq = fund * mul_oct2
  oct2_phase = 0
  oct2_mul = params[5]
  
  oct2 = Sine(freq=oct2_freq, phase=oct2_phase, mul=oct2_mul)#.out()
  
  # 2 OCTAVES & THIRD
  
  oct2_third_freq = fund * mul_oct2_third
  oct2_third_phase = 0
  oct2_third_mul = params[6]
  
  oct2_third = Sine(freq=oct2_third_freq, phase=oct2_third_phase, mul=oct2_third_mul)#.out()
  
  # 2 OCTAVES & FIFTH
  
  oct2_fifth_freq = fund * mul_oct2_fifth
  oct2_fifth_phase = 0
  oct2_fifth_mul = params[7]
  
  oct2_fifth = Sine(freq=oct2_fifth_freq, phase=oct2_fifth_phase, mul=oct2_fifth_mul)#.out()
  
  # 3 OCTAVES
  
  oct3_freq = fund * mul_oct3
  oct3_phase = 0
  oct3_mul = params[8]
  
  oct3 = Sine(freq=oct3_freq, phase=oct3_phase, mul=oct3_mul)#.out()
  
  # BANDWIDTH
  
  bandwidth = oct3_freq + 100 # added 100Hz margin for bandwidth
  
  # OSCILLATOR MIXER
  # Mixer class in pyo: http://ajaxsoundstudio.com/pyodoc/api/classes/pan.html?highlight=mixer
  
  osc_mix = Mixer(outs=1, chnls=9, time=.025)
  
  # Add all oscillators to mixer
  osc_mix.addInput(0, sub_oct)
  osc_mix.addInput(1, ref)
  osc_mix.addInput(2, fifth)
  osc_mix.addInput(3, oct1)
  osc_mix.addInput(4, oct1_fifth)
  osc_mix.addInput(5, oct2)
  osc_mix.addInput(6, oct2_third)
  osc_mix.addInput(7, oct2_fifth)
  osc_mix.addInput(8, oct3)
  
  # Add to output
  osc_mix.setAmp(0, 0, 1)
  osc_mix.setAmp(1, 0, 1)
  osc_mix.setAmp(2, 0, 1)
  osc_mix.setAmp(3, 0, 1)
  osc_mix.setAmp(4, 0, 1)
  osc_mix.setAmp(5, 0, 1)
  osc_mix.setAmp(6, 0, 1)
  osc_mix.setAmp(7, 0, 1)
  osc_mix.setAmp(8, 0, 1)
  
  # osc_mix.out()
  
  # osc_mix.ctrl()
  # s.gui(locals())
  
  # TREBLE & BASS SEPARATION
  
  bass = ButLP(osc_mix[0], freq=800, mul=1, add=0)#.out()
  treble = ButHP(osc_mix[0], freq=800, mul=1, add=0)#.out()
  
  # DELAY LINE & LFO (BASS)
  
  bass_lfo_freq = params[9]
  bass_sd_delay = params[10]
  
  bass_lfo = Sine(freq=bass_lfo_freq, phase=0, mul=1, add=0)
  bass_sd = SmoothDelay(bass, delay=bass_lfo*bass_sd_delay, feedback=0, crossfade=0.05, maxdelay=note_length, mul=1)#.out()
  
  # DELAY LINE & LFO (TREBLE)
  
  treble_lfo_freq = params[11]
  treble_sd_delay = params[12]
  
  treble_lfo = Sine(freq=treble_lfo_freq, phase=0, mul=1, add=0)
  treble_sd = SmoothDelay(treble, delay=treble_lfo*treble_sd_delay, feedback=0, crossfade=0.05, maxdelay=note_length, mul=1)#.out()
  
  # TREBLE & BASS MIXER
  
  sd_mix = Mixer(outs=1, chnls=2, time=.025)
  sd_mix.addInput(0, bass_sd)
  sd_mix.addInput(1, treble_sd)
  
  sd_mix.setAmp(0, 0, 1)
  sd_mix.setAmp(1, 0, 1)
  
  # sd_mix.out()
  
  # SIGNAL MIXER
  
  sig_mix = Mixer(outs=1, chnls=2, time=.025)
  sig_mix.addInput(0, osc_mix[0])
  sig_mix.addInput(1, sd_mix[0])
  
  sig_mix.setAmp(0, 0, 1)
  sig_mix.setAmp(1, 0, 1)
  
  # sig_mix.out()
  
  # EQUALISER (PEAK/NOTCH)
  
  eq_freq = params[13]
  eq_q = 1 + (params[14] * 499) # between 1 and 500
  eq_boost = ((params[15] - 0.5)*2)*3 # gain in dB, +/- (set to 3dB range, pos & neg)
  
  eq = EQ(sig_mix[0], freq=eq_freq*bandwidth, q=eq_q, boost=eq_boost, type=0, mul=1, add=0)
  
  # LOWPASS FILTER
  
  lp_cutoff = params[16]
  
  lp = ButHP(eq, freq=lp_cutoff*bandwidth, mul=1, add=0)#.out()
  
  # REVERB
  
  rvb_feedback = params[17]
  rvb_cutoff = params[18]
  rvb_bal = params[19]
  
  rvb = WGVerb(lp, feedback=rvb_feedback, cutoff=rvb_cutoff*bandwidth, bal=rvb_bal, mul=1, add=0).out()
  
  # In[68]:
  
  
  # --- RENDER AUDIO TO WAV FILE ---
  
  # Path to the output sound folder (root is user's home directory)
  output_folder = 'resynthesis'
  
  # Create the folder if it does not exist.
  if not os.path.isdir(output_folder):
    os.mkdir(output_folder)
  	
  # Output file duration.
  dur = note_length
  
  # Set recording parameters.
  s.recordOptions(
  	dur=dur, filename=os.path.join(output_folder, "{0}".format(name)), fileformat=0, sampletype=0,
  )
  
  s.start()
  s.shutdown()