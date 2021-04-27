import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import json

import sys

reynolds = int(sys.argv[1])
alfa = int(sys.argv[2])

job_id = sys.argv[3]
PATH = sys.argv[4]

output_path = PATH + '/output_data'

PATH = PATH + '/neural_network'

#Read CFD data
CFD_simulation = pd.read_csv(PATH + "/forceCoeff.csv",names=["Cl", "Cd", "Ca1", "Ca2", "Ce1","Ce2", "Re", "alfa"])
#Read wind tunnel data
experimental = pd.read_csv(PATH + "/NACA0012.csv",names=["Re","alfa","Cl","Cd"])


#Change this when we know how to read the input
input_NN = {'Re': [reynolds], 'alfa': [alfa], 'Cl':[None], 'Cd':[None]}
input_calc = {'Cl': [None], 'Cd': [None], 'Ca1':[None], 'Ca2':[None],'Ce1':[None], 'Ce2':[None],'Re': [reynolds], 'alfa': [alfa]}


input_data_NN = pd.DataFrame(data=input_NN)
input_data_calc= pd.DataFrame(data=input_calc)

#Normalize input
ninput_data_NN = (input_data_NN-experimental.min())/(experimental.max()-experimental.min())
ninput_data_calc = (input_data_calc - CFD_simulation.min())/(CFD_simulation.max()-CFD_simulation.min())


#Read Neural Network model
new_model = tf.keras.models.load_model(PATH + "/mymodel.h5")

#define the calculator model
calc_input = keras.Input(shape=(2,), name = "calc_input")
x = layers.Dense(4, activation="relu", name = "calc_hidden_layer1")(calc_input)
x = layers.Dense(4, activation="relu", name = "calc_hidden_layer2")(x)

calc = keras.Model(inputs=calc_input, outputs= x, name="calc")

#Copy Neural network to calculator model
calc.layers[1].set_weights(new_model.layers[1].get_weights())
calc.layers[2].set_weights(new_model.layers[2].get_weights())

#Make predictions
ninput_data_NN[["Cl", "Cd"]] = new_model.predict(ninput_data_NN[["Re", "alfa"]])
ninput_data_calc[["Ca1", "Ca2", "Ce1","Ce2"]] = calc.predict(ninput_data_calc[["Re", "alfa"]])

#Desnormalize data
output_data_NN = (experimental.max()-experimental.min())*ninput_data_NN + experimental.min()
output_data_calc = (CFD_simulation.max()-CFD_simulation.min())*ninput_data_calc + CFD_simulation.min()

#Output
output_data_NN

lift_drag = output_data_NN.to_dict()
closure_coeff = output_data_calc.to_dict()

output = {'job_id' : job_id,'re' : lift_drag['Re'][0], 'aoa' : lift_drag['alfa'][0], 'lift' : lift_drag['Cl'][0], 'drag' : lift_drag['Cd'][0], 'ca1' : closure_coeff['Ca1'][0], 'ca2' : closure_coeff['Ca2'][0], 'ce1' : closure_coeff['Ce1'][0], 'ce2' : closure_coeff['Ce2'][0]}

print(output)

with open(output_path + '/ml_output_' + job_id + '.json', 'w') as fp:
        json.dump(output, fp)
