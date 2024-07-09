import dataset

class Oracle(dataset.Dataset):
    def __init__(self, df):
        super().__init__(df)

    def predict_one_variable(self, partial_inst, var):
        # predict the most common value
        return self._get_pref_order_var(partial_inst, var)[0]

