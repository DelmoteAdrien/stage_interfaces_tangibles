import aaailearn
import random
import math
import time
import multiprocessing
import utils
import pickle

def get_data_MDL_one_instance_exact(model, instance, dataset):
    minimum = model.get_minimum_data(instance)
    return get_data_MDL_one_instance_from_compressed(minimum, dataset)

def get_data_MDL_one_instance_from_compressed(s, dataset):
    # out = math.log2(len(dataset.domains)+1) # how many variables (0 to n)
    out = utils.code_length_integer(len(s))
    out += math.log2(math.comb(len(dataset.vars), len(s)))
    for v in s:
        # out += math.log2(len(dataset.domains)) # which variable
        out += math.log2(len(dataset.domains[v]) - 1) # which value (not the optimal one)
    return out

# one prediction per order
def get_data_MDL(model, dataset):
    sum_score = utils.code_length_integer(len(dataset.dataset)) # length of dataset
    for instance in dataset.uniques:
        minimum = model.get_minimum_data(instance)
        sum_score += get_data_MDL_one_instance_from_compressed(minimum, dataset) * dataset.counts[repr(instance)] # number of occurrences
    return sum_score

def get_MDL(model, dataset):
    # return model.get_MDL(dataset) # version with log(rank)
    model.update_cpt(dataset)
    model_MDL = model.get_model_cost()
    data_MDL = get_data_MDL(model, dataset)
    # print(model_MDL, data_MDL, model_MDL+data_MDL)
    return model_MDL + data_MDL

def learn(dataset, initial_model, max_iter=None, tabu_length=100, verbose=False):
    tabu = []
    l = initial_model
    best_model = l
    best_score = get_MDL(l, dataset)
    if verbose:
        print("Initial MDL:",best_score/8,"B")
    patience = 5
    no_gain = 0
    current_iter = 0
    search = NeighborSearch(dataset)
    with multiprocessing.Pool() as pool:
        while True:
            current_iter += 1
            if max_iter is not None and current_iter > max_iter:
                break
            l,s,perturbation = modify_and_evaluate(tabu, dataset, l, pool, search)
            if s is None:
                break # no more neighbors
            # print("Candidate MDL:",s)
            if best_score is None:
                gain = 1000000 # infinity
            else:
                gain = best_score - s
            if best_score is None or s < best_score:
                best_model = l
                best_score = s
                tabu.append(perturbation)
                if len(tabu) > tabu_length:
                    tabu.pop(0) # remove the oldest element
                # print("Tabu:",tabu)
                if verbose:
                    print("Current MDL:",s/8,"B")
                # save best model so far
                l.export("last.dot")
                pickle.dump(l, open("last.pickle","wb"))
            if gain < 1: # if gain is < 1 bit, consider it has probably converged
                no_gain += 1
                if no_gain >= patience:
                    break
                if verbose:
                    print("Insist")
            else:
                no_gain = 0
        if verbose:
            print("MDL learning completed:",best_score/8,"B")
        return best_model

class NeighborSearch:
    def __init__(self, dataset):
        self.dataset = dataset

    def get_data_MDL(self, model):
        return get_MDL(model[1], self.dataset)

def modify_and_evaluate(tabu, dataset, model, pool, search):
    t = time.time()
    neighbors = model.get_neighbors(tabu, dataset)
    if len(neighbors) == 0:
        return None, None
    # print("Neighbors generation:",(time.time()-t),"s")
    t = time.time()
    # print("MDL score")
    scores = pool.map(search.get_data_MDL, neighbors)
    # print("MDL scoring:",time.time()-t,"s")
    # print("Select best")
    min_score = min(scores)
    perturbation, neighbor = neighbors[scores.index(min_score)]
    return (neighbor, min_score, perturbation)
