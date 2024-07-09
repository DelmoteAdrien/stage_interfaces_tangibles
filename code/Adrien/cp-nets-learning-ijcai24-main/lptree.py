import math
import copy
import random
import dataset
import utils

def is_compatible(instance1, instance2):
    """ check if u[V]=v[U]
    """
    for k,v in instance1.items():
        if instance2.get(k) is not None and instance2.get(k) != v:
            return False
    return True

class Node:

    def __init__(self, variables, cpt, all_vars, space_size):
        self.variables = variables
        self.all_vars = all_vars
        self.space_size = space_size
        self.cpt = cpt # list of labels
        self.domain_size = len(cpt)
        self.children = {} # Key: label. Value: child node

    def add_child(self, c, label=None):
        self.children[label] = c

    def _export(self, f):
        f.write(str(id(self))+" [label=\""+str(self.variables)+"\nCPT:"+str(self.cpt)+"\"];\n");
        for k in self.cpt:
            self._export_one_child(f, k) # if labeled edges
        self._export_one_child(f, None) # if unlabeled edge

    def _export_one_child(self, f, k):
        v = self.children.get(k)
        if v is not None:
            v._export(f)
            if k is None:
                k=""
            f.write(str(id(self))+" -> "+str(id(v))+" [label=\""+str(k)+"\"];\n");

    def get_preferred_extension(self, instance):
        for o in self.cpt:
            instance2 = {}
            utils.instantiate(instance2, self.variables, o)
            if is_compatible(instance2, instance):
                utils.instantiate(instance, self.variables, o)
                if self.children.get(o) is not None: # take the labelled edge
                    self.children.get(o).get_preferred_extension(instance)
                elif self.children.get(None) is not None: # if not, take the unlabelled edge
                    self.children.get(None).get_preferred_extension(instance)
                else:
                    assert len(instance) == len(self.all_vars)
                # if not, it’s a leaf
                return

        # value is never seen: by default, use the most preferred value
        for i in range(len(self.variables)):
            if instance.get(self.variables[i]) is None:
                instance[self.variables[i]] = self.cpt[0][i]

        if self.children.get(self.cpt[0]):
            self.children.get(self.cpt[0]).get_preferred_extension(instance)
        elif self.children.get(None) is not None: # if not, take the unlabelled edge
            self.children.get(None).get_preferred_extension(instance)
        # if not, it’s a leaf

    def get_minimum_data(self, instance):
        best = self.cpt[0]
        for o in self.cpt:
            for i in range(len(self.variables)):
                if instance.get(self.variables[i]) != o[i]:
                    break
            else:
                delta = []
                for i in range(len(self.variables)):
                    if instance[self.variables[i]] != best[i]:
                        delta.append(self.variables[i])
                if self.children.get(o) is not None: # take the labelled edge
                    d2 = self.children.get(o).get_minimum_data(instance)
                    return delta + d2
                elif self.children.get(None) is not None: # if not, take the unlabelled edge
                    d2 = self.children.get(None).get_minimum_data(instance)
                    return delta + d2
                return delta # leaf
        # no cpt is compatible: there is an unseen value.
        if self.children.get(self.cpt[0]) is not None: # take the preferred labelled edge
            return self.variables + self.children.get(self.cpt[0]).get_minimum_data(instance)
        elif self.children.get(None) is not None: # if not, take the unlabelled edge
            return self.variables + self.children.get(None).get_minimum_data(instance)
        return self.variables # leaf

class LPTree:

    def __init__(self, graph, variables):
        self.root = graph
        self.vars = variables
        # self.defaults = {}

    def update_cpt(self, dataset):
        self._update_cpt(dataset, self.root)

    def get_minimum_data(self, instance):
        return self.root.get_minimum_data(instance)

    def compress(self, instance):
        out = {}
        self.root.compress(instance,out)
        return out

    def get_preferred_extension(self, instance):
        new_inst = instance.copy()
        self.root.get_preferred_extension(new_inst)
        return new_inst

    def predict_one_variable(self, instance, var):
        return self.get_preferred_extension(instance).get(var)

    def _update_cpt(self, dataset, node, instance={}):
        node.cpt = dataset.get_pref_order(instance, node.variables)
        count = dataset.get_count(instance,node.variables).copy()
        for k,v in node.children.items():
            if k is not None:
                new_inst = instance.copy()
                utils.instantiate(new_inst, node.variables, k)
                if count.get(k) is not None:
                    del count[k]
            else:
                if len(node.children)==1:
                    new_inst = instance
                else:
                    top = list(sorted(count.items(), key=lambda item: -item[1]))
                    new_inst = instance.copy() # all counts are 0: no conditioning
                    if len(top) > 0:
                        utils.instantiate(new_inst, node.variables, top[0][0])
            self._update_cpt(dataset, v, new_inst)

    def export(self, filename):
        with open(filename, "w") as f:
            f.write("digraph G { \n");
            f.write("ordering=out;\n");
            self.root._export(f)
            f.write("}\n");
