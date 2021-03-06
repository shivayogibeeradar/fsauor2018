"""
Load data and train the model
"""
import os
import argparse
import logging
import numpy as np
import time

from collections import defaultdict
from sklearn.externals import joblib
from fgclassifier import models, classifiers
from fgclassifier.features import fm_spec
from fgclassifier.models import Baseline, Dummy
from fgclassifier.utils import read_data, save_model, get_dataset

logger = logging.getLogger(__name__)


def fm_cross_check(fmns, clss, fm_cache=None, X_train=None, X_test=None,
                   y_train=None, y_test=None, model_cls=Baseline, results={}):
    """Feature Model Cross Check"""
    avg_test_scores = results['test_avg'] = results.get(
        'test_avg', defaultdict(dict))
    test_scores = results['test'] = results.get('test', {})
    avg_train_scores = results['train_avg'] = results.get(
        'train_avg', defaultdict(dict))
    train_scores = results['train'] = results.get('train', defaultdict(dict))
    # save modes as well
    models = results['models'] = results.get('models', defaultdict(dict))
    train_time = results['train_time'] = results.get(
        'train_time', defaultdict(dict))
    test_time = results['test_time'] = results.get(
        'test_time', defaultdict(dict))

    # Test for all Feature models
    for fmn in fmns:
        logger.info('')
        logger.info(f'============ Feature Model: {fmn} ============')
        logger.info('')
        cache = fm_cache[fmn]
        # Test on all major classifiers
        for clf in clss:
            tick = time.time()
            logger.info(f'Train for {fmn} -> {clf}...')

            Classifier = getattr(classifiers, clf)
            model = model_cls((clf, Classifier), fm=cache['model'])
            model.fit(X_train, y_train)

            train_scores[fmn][clf] = model.scores(X_train, y_train)
            train_f1 = avg_train_scores[fmn][clf] = np.mean(
                train_scores[fmn][clf])

            train_time[fmn][clf] = time.time() - tick
            tick = time.time()

            test_scores[fmn][clf] = model.scores(X_test, y_test)
            test_f1 = avg_test_scores[fmn][clf] = np.mean(
                test_scores[fmn][clf])
            test_time[fmn][clf] = time.time() - tick

            logger.info(
                '-------------------------------------------------------')
            logger.info(
                f'【{fmn} -> {clf}】 Train: {train_f1:.4f}, Test: {test_f1:.4f}')
            logger.info(
                '-------------------------------------------------------')
            models[model.name] = model

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    classifier_choices = [x for x in dir(classifiers) if not x.startswith('_')]
    parser.add_argument('-m', '--model', default='Baseline',
                        help='Top-level model, the basis for classifiers.')
    parser.add_argument('-fm', '--feature-model', default='tfidf_sv',
                        choices=fm_spec.keys(),
                        help='Which model to use for feature engineering')
    parser.add_argument('-c', '--classifier', default='SVC',
                        choices=classifier_choices,
                        help='Classifier used by the model')
    parser.add_argument('--train', default=10000,
                        help='Number of training sample to use')
    parser.add_argument('--valid', default=1000,
                        help='Number of validation sample to use')
    args = parser.parse_args()

    logging.info(f'{args}')

    Model = getattr(models, args.model)
    Classifier = getattr(classifiers, args.classifier)
    X_train, Y_train = read_data(get_dataset('train'), sample_n=args.train)
    X_valid, Y_valid = read_data(get_dataset('valid'), sample_n=args.valid)
    model = Model(classifier=Classifier,
                  steps=[args.feature_model],
                  memory='data/feature_cache')

    with joblib.parallel_backend('threading', n_jobs=4):
        model.fit(X_train, Y_train)
        score = model.score(X_valid, Y_valid)
        logging.info('')
        logging.info(f'Overall F1: {score:.4f}')
        logging.info('')

    save_model(model)
