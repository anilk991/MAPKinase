import boolean2
from boolean2 import util
import json
import timeit
import matplotlib as mpl
mpl.use('Agg')  
import matplotlib.pyplot as plt
import numpy as np
import argparse as ap
from tqdm import tqdm
from glob import glob
import os
import sys

parser = ap.ArgumentParser(description='Knockout and Constitutive Activity Simulations')
parser.add_argument('--end_state', help='Set end state to be either Apoptosis or Proliferation or Growth_Arrest', required=True)
parser.add_argument('--type', help='Set the type of simulation: KO for Knockout and CA for Constitutive Activity', required=True)
args = parser.parse_args()

if args.end_state == 'Apoptosis':
	end_state = 'Apoptosis'
elif args.end_state == 'Proliferation':
	end_state = 'Proliferation'
elif args.end_state == 'Growth_Arrest':
	end_state = 'Growth_Arrest'
else:
	sys.exit('end_state value can be either Apoptosis or Proliferation or Growth_Arrest only.')

if args.type == 'KO':
	KO = True
elif args.type == 'CA':
	KO = False
else:
	sys.exit('type value can be either KO or CA only.')


#end_state = 'Apoptosis'
#KO = False
inits = glob('./input/no-stimulation.txt')
rules = file('./input/rules.txt').read()

reps = 5000
steps = 50
targets = file('./input/targets.txt').read().rstrip()
targets = targets.split('\n')

def runSimulations(text, targets, var=None, outfile=None, knockouts=True, mode='async', repeats=reps, steps=steps):
	print "\tstarting Simulations"
	data = {}
	#use the following set of targets if running the simulation for the reduced model
	#targets = ['RIP1', 'FADD', 'Caspase9']
	start = timeit.default_timer()
	if var is not None:
		assert isinstance(var, str)
	
	for target in targets:
		print "\tProcessing target", target
		if knockouts is True:
			mtext = boolean2.modify_states(text=text, turnon=['INSR'], turnoff=target)
			fname = outfile
		else:
			mtext = boolean2.modify_states(text=text, turnon=target)
			#fname = './Apoptosis_2009_Model/results_CA.json' + fn
			fname = outfile
		model = boolean2.Model(mode=mode, text=mtext)
		coll = util.Collector()
		for i in xrange(repeats):
			model.initialize(missing=util.randbool)
			model.iterate(steps=steps)
			coll.collect(states=model.states, nodes=var)
		data[target] = {'Timesteps': coll.get_averages(normalize=True)}
		data[target][var + ' AUC'] = sum(data[target]['Timesteps'][var])
				
	stop = timeit.default_timer()
	print "Completed in ", (stop - start)/60, "minutes."
	if outfile is not None:
		if not outfile.endswith('.json'):
			outfile += '.json'

		with open(outfile, 'w') as fp:
			json.dump(data, fp)
	
	return data


def make_plot(data, targets, end_state=end_state, title=None, savefig=None):
	'''
	'''
	colors = ['blue', 'green', 'red', 'purple', 'cyan', 'gray', 'salmon', 'indigo', 'brown', 'orchid', 'olive',\
			 'darkslateblue', 'violet', 'crimson', 'steelblue', 'plum', 'tab:blue', 'magenta', 'yellow', 'darkgrey',\
                         'peru', 'slateblue', 'darkorchid', 'palevioletred', 'teal']
	markers = ['o', 'v', '^', 's', 'p', 'P', '*', 'h', 'D', 'X', '|',\
			  'x', 'd', '<', '>', '1', '2', '4', '.', '8',\
                          '3', ',', '_', 'H', '+']
	
	colors = colors[:len(targets)]
	markers = markers[:len(targets)]
	plt.figure(figsize=(8,6))
	
	for target, m, c  in zip(targets, markers, colors):
		timeseries = data[target]['Timesteps'][end_state]
		plt.plot(np.array(timeseries)*100, marker=m, c=c, linestyle='-', alpha=0.7, label=target)
	plt.ylim([-10, 110])
	plt.legend(loc='upper right')
	plt.xlabel('Time Steps', fontsize=16)
	plt.ylabel('Percentage', fontsize=16)
	plt.tight_layout()
	if title is not None:
		plt.title(title, fontsize=16, fontweight="bold")
	if savefig is not None:
		plt.savefig(savefig, dpi=300)
#    plt.show()


if KO == True:
	keyword_1 = 'KO'
else:
	keyword_1 = 'CA'

if end_state == 'Apoptosis':
	keyword_2 = 'Apoptosis'
elif end_state == 'Proliferation':
	keyword_2 = 'Proliferation'
elif end_state == 'Growth_Arrest':
	keyword_2 = 'Growth_Arrest'

if not os.path.exists('./output/json_files'):
	os.mkdir('./output/json_files')

if not os.path.exists('./output/plots'):
	os.mkdir('./output/plots')

for init in tqdm(inits):
	initial = file(init).read()
	text = '\n'.join([initial, rules])
	fname = init.split('/')[-1].replace('.txt', '')
	print "Initial Condition: " + fname
	data = runSimulations(text, targets, var=end_state, \
		outfile='./output/json_files/' + keyword_1 + '_' + keyword_2 + '_' + fname, \
		knockouts=KO, repeats=reps, steps=steps)
	make_plot(data, targets, end_state=end_state, \
		savefig='./output/plots/' + keyword_1 + '_' + keyword_2 + '_' + fname + '.png')

'''
json_files = glob('./output/json_files/*.json')

for file in json_files:
	data = json.load(open(file))
	fname = file.split('/')[-1].replace('.txt', '')
	make_plot(data, targets, end_state=end_state, savefig='./output/plots/' + fname)
'''
