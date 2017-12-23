from time import time
from settings import *

import datetime
from mining.algorithms.mlearning.classifiers.NBayes import NBayes
from mining.algorithms.mlearning.classifiers.NNet import NNet
from mining.algorithms.mlearning.classifiers.KNN import KNN
from mining.algorithms.mlearning.classifiers.SVM import SVM
from sklearn.model_selection import StratifiedKFold
import mining.algorithms.mlearning.feature as f
import mining.algorithms.mlearning.persist as p
from beautifultable import BeautifulTable
import utils.plots as plots
import utils.list_utils as lu

fm = f.FeatureManager()
dm = f.DatasetManager()

class MasterAlgorithm:
    def __init__(self):
        self.features = None
        self.labels = None
        self.algorithms = None
        self.cv = None
        self.latest_scores = None

    def setup(self, fntg=MA_FEATURES_NR_TWEETS_GROUP, fnf=MA_FEATURES_NR_FEATURES, algs = MA_ALGS):
        self.features = fm.get_features_most_common(tweets=f.get_tweets(count=fntg,cbu=True), nr_features=fnf)
        self.labels = f.get_ptParser().get_labels()
        logm.info("Features: " + str(self.features))
        logm.info("Labels: " + str(self.labels))
        if algs==None or not isinstance(algs, list):
            self.algorithms = [NNet(), NBayes(), KNN(), SVM()]
        else:
            logm.info("\n[MASTER ALGORITHM] setup -> train: " + str(len(algs)) + " algorithm/s.")
            self.algorithms = algs

    def train(self, tweets_train=MA_TWEETS_TRAIN, save = MA_TRAIN_SAVE):
        logtr.info("\n========================================================================"
                   "\n[MASTER ALGORITHM] Training\n"
                   "========================================================================\n")

        if self.labels == None or self.features == None:
            self.setup()

        self.cv = StratifiedKFold(n_splits=len(self.labels), shuffle=True)
        X, Y = dm.get_ds_XY(tweets=f.get_tweets(tweets_train), features=self.features, labels_list=self.labels)

        # Uncoment to generate chart
        plots.plot_learning_curve(estimator=self.algorithms,title=None,X=X,y=Y,cv=self.cv,n_jobs=1,save_as="[" + datetime.datetime.today().strftime('%Y-%m-%d %H-%M') + "].png")

        table = BeautifulTable()
        table.column_headers = ["Iteration"] + [alg.name for alg in self.algorithms]

        i = 0
        #CROSS VALIDATION TRAIN-TEST
        for train_indices, test_indices in self.cv.split(X, Y):
            X_train, X_test = X[train_indices], X[test_indices]
            Y_train, Y_test = Y[train_indices], Y[test_indices]

            scores = [-1] * len(self.algorithms)

            for alg in self.algorithms:
                alg.train(X_train, Y_train)
                score = alg.test(X_test, Y_test)

                scores[self.algorithms.index(alg)] = score

            table.append_row([str(i)] + [str(score) for score in scores])
            i+=1

        self.latest_scores = scores

        logtr.info("\n" + str(table))

        if save:
            for alg in self.algorithms:
                p.save_model(alg.clf,join(CLASS_MODELS_DIR,alg.name))

        return scores


    def predict(self,tweets_predict=MA_TWEETS_PREDICT, load=MA_PREDICT_LOAD):
        dt = time()
        if self.labels == None or self.features == None:
            self.setup()

        logts.info("\n========================================================================"
                   "\n[MASTER ALGORITHM] Prediction\n"
                   "========================================================================\n")
        if load:
            for alg in self.algorithms:
                model = p.load_model(join(CLASS_MODELS_DIR,alg.name))
                if model != None:
                    alg.clf = model

        tweets = f.get_user_tweets(tweets_predict)
        table = BeautifulTable()
        table.column_headers = ["Index","Username"] + [alg.name for alg in self.algorithms] + ["Final (Average)"]

        final_results = []
        final_results.append(["",""] + [alg.name for alg in self.algorithms])

        if REMOVE_LIMITS:
            logts.info("Removing end tweets.")
            tweets = sorted(tweets, key=lambda x: len(x.text))
            limit_remove = int(len(tweets) * LIMITS_PERCENTAGE)
            logts.info("Removing first and last " + str(limit_remove) + " user tweets.")
            del tweets[-limit_remove:]
            del tweets[:limit_remove]

        i = 0
        for tweet in tweets:
            tmp_list = [''] * len(self.algorithms)
            for alg in self.algorithms:
                idx = self.algorithms.index(alg)
                x = dm.get_ds_X(tweet.text, self.features)
                pred, label = alg.predict_with_label(x, self.labels)
                tmp_list[idx] = label
                logm.info("\n########################################################################################################\n"
                          "[Prediction] [USER: " + tweet.username + " ] [RESULT: " + label + " ]\n" + ""
                        "############################################################################################################"
                            "\n[TEXT] \n"
                        "------------------------------------------------------------------------------------------------------------\n"
                         + tweet.text + "\n\n")

            table.append_row([i,tweet.username] + tmp_list + [self.__decideClass(tmp_list,decision='weighted')])
            final_results.append([i,tweet.username] + tmp_list)
            i+=1
        logts.info("\n" + str(table))

        results_final = [0] * len(self.labels)
        for party in list(table['Final (Average)']):
            results_final[int(self.labels.index(party))] += 1

        table_final = BeautifulTable()
        table_final.column_headers = [str(lab.decode('utf-8')) for lab in self.labels]
        table_final.append_row(results_final)

        logts.info("[Prediction Count] \n")
        logts.info("\n" + str(table_final))

        plots.plot_predictions_per_label(data = final_results, labels=self.labels,save_as=FIGURES_SAVE_AS_FORMAT)
        #plots.plot_predictions_per_alg(data = final_results, labels=self.labels,save_as=FIGURES_SAVE_AS_FORMAT)

    def __decideClass(self,data,decision=MA_DECISION):
        if decision == 'average':
            return max(set(data), key=data.count)
        elif decision =='weighted' and self.latest_scores!=None:
            res = lu.accumulate(zip(data,self.latest_scores))
            mx = lu.get_max(res)
            return mx[0]
        else:
            logts.info("Not possible to decide with WEIGHTED logic. There are no train results")
            raise Warning("Not possible to decide with WEIGHTED logic. There are no train results.")
            self.__decideClass(data,'average')


if __name__ == "__main__":
    alg = MasterAlgorithm()
    alg.setup(fntg=2, fnf=20)
    scores = alg.train(tweets_train=30,save=True)
    alg.predict(tweets_predict=10,load=False)
    logm.info("END")