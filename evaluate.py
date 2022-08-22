#!/usr/bin/env python
# coding: utf-8

# In[12]:


import spiegelib as spgl
import json


# In[13]:

def run(t, e, n):
  file_target = t
  file_estimation = e
  
  target = [spgl.AudioBuffer('18844__hammondman__tonewheel-organ-sound-samples\{0}'.format(file_target))]
  estimation = [[spgl.AudioBuffer('resynthesis\{0}'.format(file_estimation))]]
  
  evaluation = spgl.evaluation.MFCCEval(target, estimation)
  evaluation.evaluate()
  
  evaluation.save_scores_json('stats\{0}_mfcc_results.json'.format(n))
  
  
  # In[14]:
  
  
  # Returns 0 across all metrics when comparing identical audio files, as expected.
  # Outputs a dictionary in a .json file
  # Can parse directly into dictionary type: https://www.programiz.com/python-programming/json
  
  
  # In[15]:
  
  
  with open('stats\{0}_mfcc_results.json'.format(n)) as file:
    results = json.load(file)
  
  
  # In[16]:
  
  
  # Need to retrieve euclidian_distance or mean_squared_error from dictionary objects.
  # Dictionaries in Python: https://realpython.com/python-dicts/
  
  
  # In[17]:
  
  
  euclid = results['target_0']['source_0']['euclidian_distance']
  return euclid