import mdllearn
import random

class EnsembleRandom:

    def __init__(self, models):
        self.models = models

    def get_preferred_extension(self, instance):
        return random.choice(self.models).get_preferred_extension(instance)

    def predict_one_variable(self, instance, var):
        return self.get_preferred_extension(instance).get(var)


class EnsembleClosestCentroid:

    def __init__(self, models, centers, dataset):
        self.models = models
        self.centers = centers
        self.dataset = dataset

    def get_preferred_extension(self, instance):
        best_dist = None
        best_cl = None
        for n in range(len(self.centers)):
            c = self.centers.loc[n]
            dist = [str(v) != str(c[k]) for k,v in instance.items()]
            dist = sum(dist)
            if best_dist is None or dist < best_dist:
                best_cl = n
                best_dist = dist
        return self.models[best_cl].get_preferred_extension(instance)

    def predict_one_variable(self, instance, var):
        return self.get_preferred_extension(instance).get(var)


class EnsembleShortestCode:

    def __init__(self, models, dataset):
        self.models = models
        self.dataset = dataset

    def predict_one_variable(self, instance, var):
        best_s = None
        best_i = []
        for m in self.models:
            i = m.get_preferred_extension(instance)
            s = len(m.get_minimum_data(i))
            if best_s is None or s <= best_s:
                if best_s is None or s < best_s:
                    best_i = []
                    best_s = s
                best_i.append(i.get(var))
        # (in case of a tie, use the model associated to the biggest cluster)
        return max(set(best_i), key=best_i.count)

