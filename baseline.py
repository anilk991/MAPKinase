import boolean2
from boolean2 import util
import json
import argparse as ap
import sys

import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import timeit
from glob import glob
from tqdm import tqdm

parser = ap.ArgumentParser(description='Baseline Simulations for Apoptosis or Proliferation or Growth_Arrest')
parser.add_argument('--end_state', help='Set end state to be either Apoptosis or Proliferation', required=True)
args = parser.parse_args()

if args.end_state == 'Apoptosis':
	end_state = ['Apoptosis']
elif args.end_state == 'Proliferation':
	end_state = ['Proliferation']
elif args.end_state == 'Growth_Arrest':
	end_state = ['Growth_Arrest']
else:
	sys.exit('end_state value can be either Apoptosis or Proliferation or Growth_Arrest only.')


inits = glob('./input/initial_conditions/*.txt')
rules = file('./input/rules.txt').read()

reps = 5000
steps = 50

#end_state = ['Proliferation']
#end_state = ['Apoptosis']


def simulations(text, var=None, outfile=None, init_mode='random', mode='async', repeats=4500, steps=50):
	'''
	Run Boolean Network simulations and returns the state desired states
	
	Inputs:
	text: rules of the network
	var: desired states in the form of list
	outfile: saves file at the specified location in json format
	init_mode: initiation mode of missing nodes, can be random, true or false
	mode: either aysnc or sync update mode
	repeats: number of times to repeat simulations
	steps: timesteps for each simulation
	
	Outputs:
	data: A dictionary containing average state of specified nodes at each timestep along with total AUC
	'''
	print "starting Simulations"
	data = {}
	#use the following set of targets if running the simulation for the reduced model
	#targets = ['RIP1', 'FADD', 'Caspase9']
	#var should be a list of nodes in the network
	
	#print 'Starting Simulation'
	assert isinstance(var, list)
	num_states = len(var)
		
	fname = outfile
	model = boolean2.Model(mode=mode, text=text)
	coll = util.Collector()
	for i in tqdm(xrange(repeats)):
		
		if init_mode == 'random':
			model.initialize(missing=util.randbool)
		elif init_mode == 'true':
			model.initialize(missing=util.true)
		elif init_mode == 'false':
			model.initialize(missing=util.false)
		 
		model.iterate(steps=steps)

		for st in var:
			coll.collect(states=model.states, nodes=st)
			data[st] = {'Timesteps': coll.get_averages(normalize=True)[st]}
			data[st][st + ' AUC'] = sum(data[st]['Timesteps'])
		
#        print "Current Progress: ", np.round(float(i)/repeats * 100, 2), "%"

	'''
	data[target] = {'Timesteps': coll.get_averages(normalize=True)}
	data[target][var + ' AUC'] = sum(data[target]['Timesteps'][var])
	with open(fname, 'w') as fp:
		json.dump(data, fp)
	'''
	
	
	#Save timestep values in data dictionary as average of all repeats
	#data = {'Timesteps': coll.get_averages(normalize=True)}
	#Calculating Total AUC and saving in data dictionary
	#data[var + ' AUC'] = sum(data['Timesteps'][var])
	
	if outfile is not None:
		
		if not outfile.endswith('.json'):
			outfile += '.json'
			
		with open(outfile, 'w') as fp:
			json.dump(data, fp)
	
	return data


if end_state[0] == 'Apoptosis':
	keyword = 'Apoptosis'
elif end_state[0] == 'Proliferation':
	keyword = 'Proliferation'
elif end_state[0] == 'Growth_Arrest':
	keyword = 'Growth_Arrest'
else:
	raise ValueError("Invalid endstate")

start = timeit.default_timer()

for init in inits:
	initial = file(init).read()
	text = '\n'.join([initial, rules])
	fname = init.split('/')[-1].replace('.txt', '')
	print fname
	data = simulations(text, var=end_state,\
						   init_mode='random', mode='async', \
						   repeats=reps, steps=steps, outfile='./output/json_files/' + 'baseline_' + keyword + '_' + fname)

files = glob('./output/json_files/baseline_' + end_state[0] + '*.json')

colors = ['b', 'g', 'r', 'c', 'm', 'k', 'grey']
plt.figure(figsize=(10,8))
i = 0
for file in files:
	data = json.load(open(file))
	label = file.split('/')[-1]
	label = label.split('_')[-1].replace('.json', '')
	plt.plot(np.array(data[end_state[0]]['Timesteps'])*100, c=colors[i], marker='o', alpha=0.7, label=label)
	i += 1

plt.ylim([-10, 110])
plt.title('Baseline ' + end_state[0], fontweight='bold', fontsize=16)
plt.ylabel('Timesteps', fontsize=14)
plt.xlabel('Percentage', fontsize=14)
plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig('./output/plots/' + 'baseline_' + end_state[0] + '.png', dpi=300)
plt.close()

stop = timeit.default_timer()

print "\nCompleted in ", (stop - start)/60, " minutes."
