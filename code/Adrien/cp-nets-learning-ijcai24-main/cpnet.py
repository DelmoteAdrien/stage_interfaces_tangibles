import math
import dataset
import copy
import random
import utils
import lptree
import pandas as pd
import itertools

def import_from_bn(bn): # use the structure of the Bayesian network
    cpnet = CPNet(dataset.Dataset(pd.DataFrame()))
    d = {}
    for i,n in enumerate(bn.model.nodes()):
        cpnet.nodes.append(Node(n))
        d[n] = i
    for n in bn.model.nodes():
        cpd = bn.model.get_cpds(n)
        for p in cpd.get_evidence():
            cpnet.nodes[d[n]].parents.append(cpnet.nodes[d[p]])
            cpnet.nodes[d[p]].children.append(cpnet.nodes[d[n]])
        table = cpd.values.T
        dom = [cpd.state_names[v] for v in cpd.get_evidence()]
        dom = list(itertools.product(*dom))
        index = [range(0,cpd.get_cardinality([v])[v]) for v in cpd.get_evidence()]
        index = list(itertools.product(*index))
        for i, val in enumerate(dom):
            l = table[index[i]]
            order = {}
            for j,v in enumerate(l):
                order[cpd.state_names[n][j]] = l[j]
            order = list(sorted(order.items(), key=lambda item: -item[1])) # sort counts
            cpnet.nodes[d[n]].cpt[val] = [u for (u,v) in order] # keep only labels

    assert cpnet.update_topo_order() # must be acyclic
    return cpnet

class CPNet:
    """ A CP-net
    """

    def __init__(self, dataset):
        # start by initializing a separable CP-net
        self.nodes = []
        self.lptree = None
        for v in dataset.vars:
            self.nodes.append(Node(v))
        self.topo_order = list(self.nodes)
        self.update_cpt(dataset)

    def get_neighbors(self, tabu, dataset):
        cpnets = self.update_edges_neighbors(tabu, dataset)
        for (_,net) in cpnets:
            net.update_cpt(dataset)
        return cpnets

    def update_one_edge(self, i, j, dataset):
        out = []
        # already an edge
        if self.nodes[i] in self.nodes[j].children or self.nodes[j] in self.nodes[i].children:
            new_cpnet = copy.deepcopy(self) # reverse
            n1 = new_cpnet.nodes[i]
            n2 = new_cpnet.nodes[j]
            n1.cpt = {}
            n2.cpt = {}
            done = new_cpnet.reverse_edge(n1, n2, dataset)

            if done:
                out.append(new_cpnet)
            else:
                del new_cpnet
            new_cpnet2 = copy.deepcopy(self) # remove
            n1 = new_cpnet2.nodes[i]
            n2 = new_cpnet2.nodes[j]
            n1.cpt = {}
            n2.cpt = {}
            if self.nodes[i] in self.nodes[j].children:
                done = new_cpnet2.remove_child(n2, n1, dataset)
            else:
                done = new_cpnet2.remove_child(n1, n2, dataset)
            if done:
                out.append(new_cpnet2)
            else:
                del new_cpnet2
        else: # add an edge
            new_cpnet = copy.deepcopy(self) # n1 -> n2
            n1 = new_cpnet.nodes[i]
            n2 = new_cpnet.nodes[j]
            n1.cpt = {}
            n2.cpt = {}
            done = new_cpnet.add_child(n1, n2, dataset)
            if done:
                out.append(new_cpnet)
            else:
                del new_cpnet
            new_cpnet2 = copy.deepcopy(self) # n2 -> n1
            n1 = new_cpnet2.nodes[i]
            n2 = new_cpnet2.nodes[j]
            n1.cpt = {}
            n2.cpt = {}
            done = new_cpnet2.add_child(n2, n1, dataset)
            if done:
                out.append(new_cpnet2)
            else:
                del new_cpnet2
        return out

    def update_edges_neighbors(self, tabu, dataset):
        out = []
        combination = [(i,j) for i in range(len(self.nodes)) for j in range(len(self.nodes)) if i < j and (i,j) not in tabu]# and self.nodes[i] not in self.nodes[j].parents and self.nodes[j] not in self.nodes[i].parents] # only add edges
        random.shuffle(combination)
        for (i,j) in combination[:100]:
            for net in self.update_one_edge(i,j,dataset):
                for v in net.nodes:
                    out.append(((i,j),net))
        return out

    def get_roots(self):
        return [n for n in self.nodes if len(n.parents) == 0]

    def get_leaves(self):
        return [n for n in self.nodes if len(n.children) == 0]

    def reverse_edge(self, n1, n2, dataset):
        if n1 in n2.children:
            n1,n2 = n2,n1 # normalize: we want to change n1 -> n2 to n2 -> n1
        n1.children.remove(n2)
        n2.parents.remove(n1)
        n1.parents.append(n2)
        n2.children.append(n1)
        return self.update_order(dataset)

    def remove_child(self, p, c, dataset):
        p.children.remove(c)
        c.parents.remove(p)
        return self.update_order(dataset)

    def add_child(self, p, c, dataset):
        p.children.append(c)
        c.parents.append(p)
        done = self.update_order(dataset)
        if not done: # not a DAG anymore, go back to previous status
            p.children.remove(c)
            c.parents.remove(p)
        return done

    def update_cpt(self, dataset): # TODO: optimiser
        for v in self.nodes:
            if len(v.cpt) == 0:
                v.cpt = {}
                par = []
                for p in v.parents:
                    par.append(p.variable)
                dom = dataset.get_domain(par)
                for val in dom:
                    instance = {}
                    utils.instantiate(instance, par, val)
                    v.cpt[val] = dataset.get_pref_order(instance, v.variable)

    def export(self, filename):
        with open(filename, "w") as f:
            f.write("digraph G { \n");
            f.write("ordering=out;\n");
            for v in self.nodes:
                best_values = {}
                for k,val in v.cpt.items():
                    best_values[k] = val[0]
                f.write(str(id(v))+" [label=\""+str(v.variable)+"\"];\n");
                # f.write(str(id(v))+" [label=\""+str(v.variable)+"\nCOT:"+str(best_values)+"\"];\n");
                for c in v.children:
                    f.write(str(id(v))+" -> "+str(id(c))+";\n");
            f.write("}\n");

    def update_order(self, dataset):
        self.update_cpt(dataset)
        return self.update_topo_order()

    def update_topo_order(self):
        # Kahn’s algorithm
        topo_order = []
        roots = self.get_roots()
        while len(roots) > 0:
            n = roots.pop()
            topo_order.append(n)
            assert (n in self.nodes)
            for c in n.children:
                for p in c.parents:
                    if p not in topo_order:
                        break
                else:
                    roots.append(c)
        if len(topo_order) < len(self.nodes):
            # there is a cycle
            return False
        else:
            # update the topological order
            self.topo_order = topo_order
            return True

    def get_model_cost(self):
        l = utils.code_length_integer(len(self.nodes)) # how many variable
        for n in self.topo_order:
            l += utils.code_length_integer(len(n.parents)) # how many parents (between 0 to n-1 because not its own parent)
            l += math.log2(math.comb(len(self.nodes)-1, len(n.parents))) # parents encoding (not its own parent)
            l += len(n.cpt)*math.log2(len(list(n.cpt.values())[0])) # best value encoding (number of lines in the CPT * how many bits to select one value in the domain)
        return l

    # TODO: sortir de cette classe
    def get_mean_code_length(self, dataset):
        total = 0
        nb = 0
        for o in dataset.uniques:
            total += len(self.get_minimum_data(o))*dataset.counts[repr(o)]
            nb += dataset.counts[repr(o)]
        return total / nb / len(dataset.vars)

    # TODO: sortir de cette classe
    def predict_one_variable(self, instance, var):
        return self.get_preferred_extension(instance)[var]

    def get_preferred_extension(self, instance):
        instance = instance.copy()
        for n in self.topo_order:
            value = instance.get(n.variable)
            if value is None:
                value_parents = tuple([instance[p.variable] for p in n.parents])
                if n.cpt.get(value_parents) is None:
                    instance[n.variable] = None
                else:
                    instance[n.variable] = n.cpt[value_parents][0]
        return instance

    def get_minimum_data(self, instance):
        delta = []
        for n in self.topo_order:
            value_parents = tuple([instance[p.variable] for p in n.parents])
            if n.cpt.get(value_parents) is None: # parent value was never seen in data
                delta.append(n.variable)
            elif instance[n.variable] != n.cpt[value_parents][0]:
                delta.append(n.variable)
        return delta

class Node:

    def __init__(self, variable):
        self.variable = variable
        self.cpt = {} # dict. Key: parent value. Value: list of values
        self.children = []
        self.parents = []
