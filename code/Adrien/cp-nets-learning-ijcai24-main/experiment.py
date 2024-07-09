import random
import multiprocessing
import pickle
import os
import time
import pgmpy.models
import csv
import sklearn.model_selection
import pandas as pd

import lptree
import dataset
import cpnet
import mdllearn
import bayesian_network
import oracle
import ensemble
import aaailearn

def read_csv_train_test(file):
     with open(file, mode='r') as f:
        reader = csv.DictReader(f)
        d = []
        for row in reader:
            d.append(row)
        train, test = sklearn.model_selection.train_test_split(d, test_size=0.2, random_state=42)
        return pd.DataFrame(train), pd.DataFrame(test)

def run_expe_recom(ds_name):
    csv_train, csv_test = read_csv_train_test("datasets/renault_"+ds_name+".csv")
    h_train = dataset.Dataset(csv_train)
    h_test = dataset.Dataset(csv_test)

    

    # Bayesian network
    print("Bayesian network")
    if os.path.isfile("models/"+ds_name+"-bn.bif"):
        bn = bayesian_network.BN.load("models/"+ds_name+"-bn.bif", csv_train)
    else:
        print("Learn BN")
        bn = bayesian_network.BN()
        bn.fit(csv_train)
        bn.model.save("models/"+ds_name+"-bn.bif")
    evaluate(h_test, bn)

    # Separable CP-net
    print("Separable CP-net")
    separable_net = cpnet.CPNet(h_train)
    evaluate(h_test, separable_net)

    # CP-net
    print("CP-net (BN)")
    net = cpnet.import_from_bn(bn)
    evaluate(h_test, net)
    # net.export("models/cpnet-"+ds_name+"-bn.dot")

    print("CP-net (BN+HC)")
    if os.path.isfile("models/cpnet-"+ds_name+"-bn+hc.pickle"):
        net = pickle.load(open("models/cpnet-"+ds_name+"-bn+hc.pickle","rb"))
    else:
        print("Learn CP-net")
        net = mdllearn.learn(h_train, net, verbose=True)
        pickle.dump(net, open("models/cpnet-"+ds_name+"-bn+hc.pickle","wb"))
    evaluate(h_test, net)
    # net.export("models/cpnet-"+ds_name+"-bn+hc.dot")

    print("CP-net (HC)")
    if os.path.isfile("models/cpnet-"+ds_name+"-hc.pickle"):
        net = pickle.load(open("models/cpnet-"+ds_name+"-hc.pickle","rb"))
    else:
        print("Learn CP-net")
        net = mdllearn.learn(h_train, separable_net, verbose=True)
        pickle.dump(net, open("models/cpnet-"+ds_name+"-hc.pickle","wb"))
    evaluate(h_test, net)
    # net.export("models/cpnet-"+ds_name+"-hc.dot")

    # LP-trees
    print("LP-tree learning (AAAI'18)")
    l = aaailearn.learn_lptree(h_train)
    evaluate(h_test, l)

    nb_clusters = 3
    clusters, centers = h_train.kmeans_hamming_split(nb_clusters)

    # LP-trees (3 clusters)
    print('Clustering with "shortest code" heuristic,',nb_clusters,"LP-trees")
    models = []
    for hc in clusters:
        models.append(aaailearn.learn_lptree(hc))
    e = ensemble.EnsembleShortestCode(models, h_train)
    evaluate(h_test, e)

    # CP-nets (3 clusters)
    if os.path.isfile("models/clusters-cpnets-"+ds_name+".pickle"):
        models = pickle.load(open("models/clusters-cpnets-"+ds_name+".pickle","rb"))
    else:
        models = []
        print("Learn CP-net")
        for hc in clusters:
            bn = bayesian_network.BN()
            bn.fit(hc.df)
            net = cpnet.import_from_bn(bn)
            net = mdllearn.learn(hc, net, verbose=True)
            models.append(net)
        pickle.dump(models, open("models/clusters-cpnets-"+ds_name+".pickle","wb"))

    print("Clustering with \"shortest code\" heuristic,",nb_clusters,"CP-nets")
    e = ensemble.EnsembleShortestCode(models, h_train)
    evaluate(h_test, e)
    print("Clustering with \"closest centroid\" heuristic,",nb_clusters,"CP-nets")
    e = ensemble.EnsembleClosestCentroid(models, centers, h_train)
    evaluate(h_test, e)
    print("Clustering with \"random\" heuristic,",nb_clusters,"CP-nets")
    e = ensemble.EnsembleRandom(models)
    evaluate(h_test, e)

class ConfigExperiment:
    def __init__(self, test_set, model):
        self.test_set = test_set
        self.model = model

    def run_map(self, instance):
        var_order = self.test_set.vars.copy()
        successes = [0]*len(self.test_set.vars)
        times = [0]*len(self.test_set.vars)
        nb_iter = 100
        for _ in range(nb_iter):
            random.shuffle(var_order)
            partial_inst = {}
            i = 0
            for v in var_order:
                t = time.process_time()
                value = self.model.predict_one_variable(partial_inst, v)
                times[i] += time.process_time() - t
                if value == instance[v]: # correct
                    successes[i] += 1 # found it
                partial_inst[v] = instance[v] # give another clue
                i += 1
        successes = [v/nb_iter for v in successes]
        times = [t/nb_iter for t in times]
        return successes, times

def evaluate(test_set, model):
    correct = [0]*len(test_set.vars)
    total = [0]*len(test_set.vars)
    var_order = test_set.vars.copy()
    config_expe = ConfigExperiment(test_set, model)
    with multiprocessing.Pool() as pool:
        successes = pool.map(config_expe.run_map, test_set.dataset)
        successes,times = zip(*successes)
    l = [sum(i)/len(test_set.dataset) for i in zip(*successes)]
    t = [sum(i)/len(test_set.dataset) for i in zip(*times)]
    print("Accuracy:",l)
    print("Time:",t)
    print("Mean accuracy:",100*sum(l)/len(l),"%")
    print("Mean time:",sum(t)/len(t),"s")
    return sum(l)/len(l) # return mean accuracy

if __name__ == "__main__":
    print("DATASET: SMALL")
    run_expe_recom("small")
    print("DATASET: MEDIUM")
    run_expe_recom("medium")
    print("DATASET: BIG")
    run_expe_recom("big")
