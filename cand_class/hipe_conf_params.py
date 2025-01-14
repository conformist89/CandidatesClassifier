from hipe4ml.model_handler import ModelHandler
from dataclasses import dataclass
import xgboost as xgb

import matplotlib.pyplot as plt
from hipe4ml import plot_utils

import xgboost as xgb


@dataclass
class XGBmodel():
    features_for_train: list
    hyper_pars_ranges: dict
    train_test_data: list
    output_path : str
    __model_hdl: ModelHandler = (None, None, None)
    metrics: str = 'roc_auc'
    nfold: int = 3
    init_points: int = 1
    n_iter: int = 2
    n_jobs: int = -1




    def modelBO(self):
        model_clf = xgb.XGBClassifier()
        self.__model_hdl = ModelHandler(model_clf, self.features_for_train)
        self.__model_hdl.optimize_params_bayes(self.train_test_data, self.hyper_pars_ranges,
         self.metrics, self.nfold, self.init_points, self.n_iter, self.n_jobs)



    def train_test_pred(self):
        self.__model_hdl.train_test_model(self.train_test_data)

        y_pred_train = self.__model_hdl.predict(self.train_test_data[0], False)
        y_pred_test = self.__model_hdl.predict(self.train_test_data[2], False)


        return y_pred_train, y_pred_test


    def save_predictions(self, filename):
        print(self.__model_hdl.get_original_model())
        self.__model_hdl.dump_original_model(self.output_path+'/'+filename, xgb_format=False)


    def load_model(self, filename):
        self.__model_hdl.load_model_handler(filename)


    def get_mode_booster(self):
        return self.__model_hdl.model


    def plot_dists(self):

        leg_labels = ['background', 'signal']
        ml_out_fig = plot_utils.plot_output_train_test(self.__model_hdl, self.train_test_data, 100,
                                               False, leg_labels, True, density=True)

        plt.savefig(str(self.output_path)+'/thresholds.png')
