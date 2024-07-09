import csv
import itertools
import pandas as pd
import numpy as np
import sklearn.cluster
import sklearn.model_selection

class Dataset:

    def __init__(self, df):
        self.vars = list(df.columns)
        self.memoize = {}
        self.domains = {}
        self.uniques = []
        self.counts = {}
        self.df = df
        self.dataset = df.to_dict('records')
        self.space_size = 1

        # uniques_df includes the number of occurrences as well
        self.uniques_df = df.groupby(df.columns.tolist(), as_index=False).size()
        self.uniques = self.uniques_df.to_dict('records')
        for o in self.uniques:
            self.counts[repr(o)] = o.pop("size")

        for v in self.vars:
            self.domains[v] = df[v].unique()
            self.space_size *= len(self.domains[v])

    def kmeans_hamming_split(self, nb_clusters):
        """ Use Hamming distance
        """
        best_labels = None
        best_centroids = None
        best_score = None
        for _ in range(50):
            centroids = self.df.loc[np.random.choice(len(self.df), nb_clusters, replace=False)]
            prev_labels = None
            labels = np.zeros(len(self.df))
            no_score = False
            while not np.all(labels == prev_labels):
                prev_labels = labels
                new_labels = np.apply_along_axis(lambda x: np.argmin(np.sum(centroids != x, axis=1)), 1, self.df)
                uniques = np.unique(new_labels, return_counts = True)
                if len(uniques[0]) < nb_clusters:
                    labels = prev_labels
                    no_score = True
                    break
                labels = new_labels
                centroids = pd.concat([self.df.loc[labels == k].mode() for k in range(nb_clusters)], ignore_index = True)
            if no_score:
                continue
            score = sum([(self.df.loc[labels == k] != centroids.loc[k]).sum().sum() for k in range(nb_clusters)])
            if best_score is None or score < best_score:
                best_score = score
                best_centroids = centroids
                best_labels = labels

        out = []
        for k in range(nb_clusters):
            data = self.df.loc[best_labels == k]
            h = Dataset(data)
            h.domains = self.domains.copy()
            h.space_size = self.space_size
            out.append(h)
        return out, best_centroids

    def get_domain_size(self, variables):
        out = 1
        for v in variables:
            out *= max(2,len(self.domains[v])) # maybe we didn’t see all values, but all variables should have a least two values
        return out

    def get_domain(self, variables):
        domains = [self.domains[v] for v in variables]
        return list(itertools.product(*domains))

    def get_count(self, instance, variables):
        out = self.memoize.get((tuple(sorted(instance.items())), tuple(variables)))
        if out is not None:
            return out
        if len(instance)>0:
            m = True
            for v in instance.keys():
                m = m & (self.uniques_df[v] == instance[v])
            comp = self.uniques_df[m]
        else:
            comp = self.uniques_df
        proj = comp.groupby(variables).agg(size=("size", "sum")).to_dict()["size"]
        self.memoize[(tuple(sorted(instance.items())),tuple(variables))] = proj
        return proj

    def get_pref_order(self, instance, variables):
        if type(variables) == list:
            return self._get_pref_order_list(instance, variables)
        return self._get_pref_order_var(instance, variables)

    def _get_pref_order_list(self, instance, variables):
        order = self.get_count(instance, variables) # get counts
        order = list(sorted(order.items(), key=lambda item: -item[1])) # sort counts
        if len(variables)==1:
            l = [(u,) for (u,v) in order] # keep only labels, tuple-ify
        else:
            l = [u for (u,v) in order] # keep only labels
        l += [d for d in self.get_domain(variables) if d not in l] # add missing labels
        return l

    def _get_pref_order_var(self, instance, variable):
        order = self.get_count(instance, [variable]) # get counts
        order = list(sorted(order.items(), key=lambda item: -item[1])) # sort counts
        l = [u for (u,v) in order] # keep only labels
        l += [d for d in self.domains[variable] if d not in l] # add missing labels
        return l


