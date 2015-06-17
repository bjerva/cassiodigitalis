#!/usr/bin/env python

'''
Map person-concept relations
'''

import numpy as np
from scipy.spatial.distance import cdist, cosine
from sklearn.preprocessing import normalize
import cPickle
from sys import argv
from collections import defaultdict


def read_w2vec(fname):
    with open(argv[1]+'.pickle', 'rb') as in_f:
        words = cPickle.load(in_f)

    vectors = np.load(argv[1]+'.npy')

    return words, vectors


def read_poi(fname, vectors, words_to_idx):
    with open(fname, 'r') as in_f:
        poi = [line.strip().lower().split('|') for line in in_f]

    poi_vecs = []
    for person in poi:
        poi_vecs.append([])
        for name in person:
            if name in words_to_idx:
                poi_vecs[-1].append(vectors[words_to_idx[name]])

    return poi, poi_vecs

def read_concepts(fname, vectors, words_to_idx):
    concepts = defaultdict(list)
    concepts_vecs = defaultdict(list)
    with open(fname, 'r') as in_f:
        for line in in_f:
            fields = line.lower().strip().split(',')
            #print fields
            #raw_input()
            concepts[fields[0]] = [word for word in fields[1:] if word in words_to_idx]
            for word in concepts[fields[0]]:
                concepts_vecs[fields[0]].append(vectors[words_to_idx[word]])

    return concepts, concepts_vecs


if __name__ == '__main__':
    w2vec_fname = argv[1]
    words, vectors = read_w2vec(w2vec_fname)
    words_to_idx = dict([(word, idx) for idx, word in enumerate(words)])

    poi, poi_vecs = read_poi(argv[2], vectors, words_to_idx)
    concepts, concept_vecs = read_concepts(argv[3], vectors, words_to_idx)

    print poi
    print concepts

    distance_dict = defaultdict(list)
    for idx, poi_vec in enumerate(poi_vecs):
        if len(poi_vec) == 0: continue
        current_poi = poi[idx][0]
        current_poi_vec = poi_vec[0]
        for v in poi_vec[1:]:
            current_poi_vec += v

        for key, concept_vec in concept_vecs.iteritems():
            dists = []
            for vec in concept_vec:
                dists.append(cosine(current_poi_vec, vec))

            mean = sum(dists) / len(dists)
            minim = min(dists)

            distance_dict[current_poi].append((key, minim))


    output = []
    for key, value in sorted(distance_dict.items(), key=lambda x:x[0]):
        if len(output) == 0:
            header = 'name\t'
            for concept, distance in sorted(value, key=lambda x:x[0]):
                header += concept + '\t'
            header += '\n'
            output.append(header)
        print key, sorted(value, key=lambda x:x[1])
        rep = key
        dists = [distance for concept, distance in sorted(value, key=lambda x:x[0])]
        dists = [distance if distance > 0.4 else max(dists)+0.1 for distance in dists]
        dists = np.asarray(dists)
        dists = np.log2(dists)
        norm = dists / sum(dists)
        norm = 1 - norm
        norm = norm / sum(norm)
        norm = 1 - norm
        print dists
        print norm
        for idx, (concept, distance) in enumerate(sorted(value, key=lambda x:x[0])):
            rep += '\t{0}'.format(norm[idx])

        rep += '\n'
        output.append(rep)


    print len(output[0].split('\t'))
    with open(argv[4], 'w') as out_f:
        #out_f.write('person\t')
        #for i in xrange((len(output[0].split('\t'))-1) / 2):
        #    out_f.write('attr.{0}\tscore{0}\t'.format(i+1))
        out_f.write('\n')
        for rep in output:
            out_f.write(rep)
