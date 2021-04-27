from subprocess import call
from pathlib import Path
import shutil
import time
import sys 
import os
import subprocess
import json

def edit_closure_coeff(re, aoa, ca1, ca2, ce1, ce2, path):

    with open(path + '/parameters', 'r') as file:
    # read a list of lines into data
        data = file.readlines()

    data[14] = 'Re             {re};\n'.format(re=re)
    data[20] = 'AOA             {aoa};\n'.format(aoa=aoa)
    data[23] = 'ca1             {ca1};\n'.format(ca1=ca1)
    data[24] = 'ca2             {ca2};\n'.format(ca2=ca2)
    data[25] = 'ce1             {ce1};\n'.format(ce1=ce1)
    data[26] = 'ce2             {ce2};\n'.format(ce2=ce2)

    with open(path + '/parameters', 'w') as file:
        file.writelines( data )

 
def fetch_output(path):

    output_dir = ''

    folders = os.listdir(path)
    folders = [x for x in folders if x.isnumeric() and x != '0']
    if folders:
        output_dir = folders[0]
    else:
        print('Error with openfoam run. Folders not created !')
        return -1


    print('Output Exists')
    time.sleep(2)

    with open(path + '/' + output_dir + '/uniform/functionObjects/functionObjectProperties', 'r') as file:
    # read a list of lines into data
        data = file.readlines()

    cl = ''
    cd = ''

    for line in data:
        line = line.split()

        if len(line) == 2:
            if line[0] == 'Cl':
                cl = line[1].replace(';','')
            elif line[0] == 'Cd':
                cd = line[1].replace(';','')
    

    output_dict = {'lift' : cl, 'drag' : cd}

    return output_dict


def run_openfoam(re, aoa, ca1, ca2, ce1, ce2, path):
    edit_closure_coeff(re, aoa, ca1, ca2, ce1, ce2, path)
    subprocess.call('simpleFoam', cwd = path)
    output = fetch_output(path)
    return output