#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
from geneticalgorithm import geneticalgorithm as ga

import wave
import contextlib
from audiolazy import lazy_midi

import os
import json

import hammond
import evaluate

from datetime import datetime

# In[2]:


samples = os.listdir('18844__hammondman__tonewheel-organ-sound-samples')

for sample in samples:
	if sample.endswith('.wav'):


		# In[3]:

		num_params = 20
		target_fn = sample
		resynth_fn = 'resynth_' + target_fn    
    
		note = target_fn[20:22] # indices 20 & 21 for note name from sample filenames, e.g. a4
		
		if not os.path.isfile('log.txt'):
			open('log.txt', 'a').close()
		
		with open('log.txt', 'r') as f:
			if note in f.read():
				f.close()
				print('programmer: Note ' + note + ' already resynthesised.')
				continue
    
		print('programmer: Continuing with new note ' + note + '.')
		
		begin = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")

		with contextlib.closing(wave.open('18844__hammondman__tonewheel-organ-sound-samples/{0}'.format(target_fn), 'r')) as f:
			frames = f.getnframes()
			rate = f.getframerate()
			duration = frames / float(rate)
			duration = duration - 512*(1/44100)

		frequency = lazy_midi.str2freq(note) # fundamental frequency for resynthesis


		# In[4]:


		def errorfunc(X):
			hammond.render(resynth_fn, X, frequency, duration)
			return evaluate.run(target_fn, resynth_fn, note)

		# defines the range of each individual parameter in the prediction
		varbound = np.array([[0,1]]*num_params) # 20 parameters, each within range 0-1


		# In[5]:


		algorithm_param = {'max_num_iteration': None, 'population_size':500, 'mutation_probability':(1/num_params), 'elit_ratio': 0.01, 'crossover_probability': 0.5, 'parents_portion': 0.3, 'crossover_type':'uniform', 'max_iteration_without_improv':None}


		# In[6]:


		model = ga(function=errorfunc, function_timeout=259200, dimension=num_params, variable_type='real', variable_boundaries=varbound,
				   algorithm_parameters=algorithm_param)
		model.run()

		# function: should return error score, loss, etc.
		# dimension: number of parameters to be estimated within a list
		# variable_type: type for parameters (real, int, etc.)
		# variable_boundaries: range for each parameter in list, see varbound definition in prev. cell


		# In[7]:


		convergence=model.report # list containing error scores returned for each iteration
		solution=model.output_dict # best candidate and associated error score

		# output_dict is a dictionary including the best set of variables found
		# and the value of the given function associated to it ({'variable': , 'function': }).
		# report is a list including the convergence of the algorithm over iterations


		# In[8]:

		end = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")

		# prepare and open file

		txtpath = 'stats'
		txtname = '{0}.txt'.format(note)
		fulltxt = os.path.join(txtpath, txtname)

		txtfile = open(fulltxt, 'w')


		# In[9]:

		# write begin and end timestamps to file
		
		txtfile.write('Start: ' + begin + '\n')
		txtfile.write('Stop: ' + end + '\n\n')

		# write convergence (list) to file

		for element in convergence:
		  txtfile.write(str(element) + ', ')
		txtfile.write('\n\n')


		# In[10]:


		# write solution (dict) to file

		solution['variable'] = solution['variable'].tolist() # convert np.array to list

		txtfile.write(json.dumps(solution))
		txtfile.close()


		# In[11]:


		# keep track of completed resyntheses

		log = open('log.txt', 'a')
		log.write('\nCompleted: ' + note)
		log.close()