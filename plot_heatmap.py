#!/usr/bin/env python

'''
Plots person-concept heatmaps

'''

import plotly.plotly as py
from plotly.graph_objs import *
from sys import argv

def swap(data):
    tmp = data[4][:]
    data[4] = data[0][:]
    data[0] = tmp[:]

    return data

def swap2(data):
    for person in data:
        tmp = person[4]
        person[4] = person[0]
        person[0] = tmp

    return data

if __name__ == '__main__':

    out_fname = argv[1]
    if len(argv) == 3:
        grp_number = argv[2]

        group1 = 'Alaricus, Odovacer, Theodericus, Athalaricus, Theodahadus, Anastasius, Iustinianus, Theodora'.lower().split(', ')
        group2 = 'Agapetus, Cassiodorus, Liberius, Symmachus, Boethius, Patricius'.lower().split(', ')
        current_group = group1 if grp_number == '1' else group2
    elif len(argv) == 2:
        grp_number = 3
        current_group = 'Vergilius, Cicero'.lower().split(', ')
    else:
        print 'Usage: python plot_heatmap.py <poi_scores_file> <group number>'

    with open(out_fname, 'r') as in_f:
        in_f.readline()
        header = in_f.readline().strip().split()[1:]
        labels = []
        data = []
        for line in in_f:
            fields = line.split()
            if fields[0] in current_group:
                labels.append(fields[0])
                data.append([float(i) for i in fields[1:]])


    # Reorder columns
    header = swap(header)
    data = swap2(data)

    data = Data([
        Heatmap(
            z=data,
            x=header,
            y=labels
        )
    ])
    plot_url = py.plot(data, filename='cassiodigitalis-person-concept-mapping-{0}'.format(grp_number))
