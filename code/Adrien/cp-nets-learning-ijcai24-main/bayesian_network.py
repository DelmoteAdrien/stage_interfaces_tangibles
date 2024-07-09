import pgmpy
import pgmpy.models
import pgmpy.estimators
import pgmpy.inference

class BN:
    def load(file, csv):
        bn = BN()
        bn.model = pgmpy.models.BayesianNetwork.load(file)
        bn.vars = list(csv.columns)
        return bn

    def __init__(self):
        self.model = None
        self.vars = None
        self.map = True

    def use_map(self, use_map):
        self.map = use_map

    def fit(self, dataset, max_iter=200):
        scoring_method = pgmpy.estimators.BicScore(data=dataset)
        est = pgmpy.estimators.HillClimbSearch(data=dataset)
        self.model = est.estimate(scoring_method=scoring_method, max_indegree=3, show_progress=True, max_iter=max_iter)
        self.model = pgmpy.models.BayesianNetwork(self.model)
        self.model.fit(data=dataset,estimator=pgmpy.estimators.BayesianEstimator,prior_type="K2")
        self.vars = list(dataset.columns)

    def predict_one_variable(self, partial_inst, var):
        inference = pgmpy.inference.VariableElimination(self.model)
        if self.map:
            try:
                val = inference.map_query(variables=[var], evidence=partial_inst, show_progress=False)
                return val[var]
            except:
                return None
        else:
            return self.get_preferred_extension(partial_inst)[var]
