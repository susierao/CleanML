""" Generate tables from results"""
import json
import pandas as pd
import numpy as np
import utils
from collections import defaultdict
from scipy.stats import ttest_rel
import config
import os
from matplotlib import pyplot as plt

def group(result, idx):
    """ Combine result from different experiments into a list

        Args:
            result (dict): result dict
                             key (string): dataset_name/split_seed/error_type/train_file/model_name/seed
                             value (dict): metric_name: metric
            idx: the index of key component by which the result is grouped 
    """
    # get all seeds
    seeds = list({k.split('/')[idx] for k in result.keys()})
    
    new_result = {}
    for s in seeds:
        for k, v in result.items():
            old_key = k.split('/')
            seed = old_key[idx]

            if s == seed:
                # new key
                key = tuple([old_key[i] for i in range(len(old_key)) if i != idx])

                # new value
                if key not in new_result.keys():
                    new_result[key] = defaultdict(list)
                
                # apppend results
                for vk, vv in v.items():
                    # don't include best param and seeds saved in result
                    if vk not in ["best_params", "seeds"]:
                        new_result[key][vk].append(vv)
    return new_result

def reduce_by_mean(result):
    """ Reduce a list of results from different experiments into a single result by mean
        
        Args:
        result (dict): result dict
                         key (tuple): (dataset_name, error_type, train_file, model_name)
                         value (dict): metric_name: metric lists
    """
    new_result = {}
    for k, v in result.items():
        new_value = {}
        for vk, vv in v.items():
            new_value[vk] = np.mean(vv)
        new_result[k] = new_value
    return new_result

def is_metric_f1(dataset_name):
    dataset = utils.get_dataset(dataset_name)
    return ('class_imbalance' in dataset.keys() and dataset['class_imbalance'])

def get_metric_name(dataset_name, test_file):
    if is_metric_f1(dataset_name):
        metric = test_file + "_test_f1"
    else:
        metric = test_file + "_test_acc"
    return metric

def get_four_metrics(result, error_type, file_types):
    """ Get four metrics for all datasets in a table (pandas.DataFrame)

        Args:
            result (dict): result dict
            error_type (string): error type
            file_types (list): names of two types of train or test files
    """

    four_metrics = {}
    for (dataset, split_seed, error, train_file, model), v in result.items():
        if error == error_type and train_file in file_types:
            for test_file in file_types:
                metric_name = get_metric_name(dataset, test_file)
                metric = v[metric_name]
                four_metrics[(dataset, split_seed, train_file, model, test_file)] = metric
    four_metrics = utils.dict_to_df(four_metrics, [0, 2, 1], [3, 4])
    return four_metrics

def compare_four_metrics(four_metrics, file_types, compare_method):
    """ Compute the relative difference between four metrics

        Args:
            four_metrics (pandas.DataFrame): four metrics
            file_types (list): names of two types of train or test files
            compare_method (fn): function to compare two metrics
    """
    A = lambda m: m.loc[file_types[0], file_types[0]]
    B = lambda m: m.loc[file_types[0], file_types[1]]
    C = lambda m: m.loc[file_types[1], file_types[0]]
    D = lambda m: m.loc[file_types[1], file_types[1]]
    AB = lambda m: compare_method(A(m), B(m))
    AC = lambda m: compare_method(A(m), C(m))
    CD = lambda m: compare_method(C(m), D(m))
    BD = lambda m: compare_method(B(m), D(m))

    comparison = {}
    datasets = list(set(four_metrics.index.get_level_values(0)))
    models = list(set(four_metrics.columns.get_level_values(0)))
    for dataset in datasets:
        for model in models:
            m = four_metrics.loc[dataset, model]
            comparison[(dataset, model, "AB")] = AB(m)
            comparison[(dataset, model, "CD")] = CD(m)
            comparison[(dataset, model, "AC")] = AC(m)
            comparison[(dataset, model, "BD")] = BD(m)
    comparison = utils.dict_to_df(comparison, [0, 1], [2])
    return comparison

def t_test(a, b):
    n_a = len(a)
    n_b = len(b)
    n = min(n_a, n_b)
    t, p = ttest_rel(a[:n], b[:n])
    return (t, p)

def compare_dup_incon(result, error, compare_method):
    """ Comparison for duplicates and inconsistency
        Args:
            error: "duplicates or inconsistency"

    """
    file_types = ["dirty", "clean"]
    four_metrics = get_four_metrics(result, error, file_types)
    comparison = compare_four_metrics(four_metrics, file_types, compare_method)
    comparisons = {"clean": comparison}
    metrics = {"clean": four_metrics}
    return comparisons, metrics

def compare_out(result, compare_method):
    """ Comparison for outliers"""
    clean_methods = ["clean_SD_delete", "clean_SD_impute_mean_dummy", "clean_SD_impute_median_dummy", "clean_SD_impute_mode_dummy",
                    "clean_IQR_delete", "clean_IQR_impute_mean_dummy", "clean_IQR_impute_median_dummy", "clean_IQR_impute_mode_dummy", 
                    "clean_iso_forest_delete", "clean_iso_forest_impute_mean_dummy", "clean_iso_forest_impute_median_dummy", "clean_iso_forest_impute_mode_dummy"]
    metrics = {}
    comparisons = {}
    for method in clean_methods:
        file_types = ['dirty', method]
        four_metrics = get_four_metrics(result, "outliers", file_types)
        comparison = compare_four_metrics(four_metrics, file_types, compare_method)
        metrics[method] = four_metrics
        comparisons[method] = comparison
    return comparisons, metrics

def compare_mv(result, compare_method):
    """ Comparison for missing values"""
    impute_methods = ["impute_mean_mode", "impute_mean_dummy", 
                      "impute_median_mode", "impute_median_dummy", 
                      "impute_mode_mode", "impute_mode_dummy"]
    metrics = {}
    comparisons = {}
    for method in impute_methods:
        file_types = ['delete', method]
        four_metrics = get_four_metrics(result, "missing_values", file_types)
        comparison = compare_four_metrics(four_metrics, file_types, compare_method)
        metrics[method] = four_metrics
        comparisons[method] = comparison
    return comparisons, metrics

def compare_mislabel(result, compare_method):
    """ Comparison for mislabel"""
    inject_methods = ["dirty_uniform", "dirty_major", "dirty_minor"]

    comparisons = {}
    metrics = {}
    for method in inject_methods:
        file_types = [method, "clean"]
        four_metrics = get_four_metrics(result, "mislabel", file_types)
        comparison = compare_four_metrics(four_metrics, file_types, compare_method)
        metrics[method] = four_metrics
        comparisons[method] = comparison
    return comparisons, metrics

def save_dfs(dfs, save_dir):
    directory = os.path.dirname(save_dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
    writer = pd.ExcelWriter(save_dir)
    for k, df in dfs.items():
        if "iso_forest" in k:
            k = k.replace("iso_forest", "ISO")
        df.to_excel(writer, '%s'%k)
    writer.save()

if __name__ == '__main__':
    # result = utils.load_result()
    # result = group(result, 5)
    # result = reduce_by_mean(result)
    # mv_comp, mv_metrics = compare_mv(result, t_test)
    # out_comp, out_metrics = compare_out(result, t_test)
    # ml_comp,  ml_metrics = compare_mislabel(result, t_test)
    # dup_comp, dup_metrics = compare_dup_incon(result, "duplicates", t_test)
    # # incon_comp, incon_metrics = compare_dup_incon(result, "inconsistency")
    # save_dfs(mv_comp, "./table/t_test/missing_values.xls")
    # save_dfs(out_comp, "./table/t_test/outliers.xls")
    # save_dfs(ml_comp, "./table/t_test/mislabel.xls")
    # save_dfs(dup_comp, "./table/t_test/duplicates.xls")

    # save_dfs(mv_metrics, "./table/four_metrics/missing_values.xls")
    # save_dfs(out_metrics, "./table/four_metrics/outliers.xls")
    # save_dfs(ml_metrics, "./table/four_metrics/mislabel.xls")
    # save_dfs(dup_metrics, "./table/four_metrics/duplicates.xls")

    # save_comparisons(incon, "./table/t_test/inconsistency")

    # four_metrics = get_four_metrics(result, 'missing_values', ['delete', 'impute_mean_mode'])
    # print(compare_four_metrics(four_metrics, ['delete', 'impute_mean_mode'], ttest_rel))

    a = [0.38, 0.356666667,0.333333333,0.313333333,0.313333333,0.356666667,0.313333333,0.353333333,0.373333333,0.283333333,0.376666667,0.32,0.38,0.29,0.276666667,0.483333333,0.31,0.343333333,0.316666667]
    b = [0.39, 0.363333333, 0.443333333,0.313333333,0.313333333,0.36,0.3,0.353333333,0.376666667,0.276666667,0.336666667,0.32,0.38,0.29,0.276666667,0.483333333,0.306666667,0.343333333,0.316666667]
    plt.plot(a, label="D")
    plt.plot(b, label="B")
    print(t_test(a, b))
    plt.legend()

    a = [0.819333333,0.822666667,0.884666667,0.871333333,0.86,0.820666667,0.820666667,0.858666667,0.842666667,0.858666667,0.845333333,0.869333333,0.818,0.814,0.852,0.829333333,0.859333333,0.835333333,0.843333333]
    b = [0.814,0.824,0.882666667,0.868666667,0.856666667,0.812666667,0.824666667,0.857333333,0.836,0.861333333,0.841333333,0.862,0.806666667,0.810666667,0.859333333,0.825333333,0.856,0.832666667,0.836]
    plt.figure()
    plt.plot(a, label="D")
    plt.plot(b, label="B")
    print(t_test(a, b))
    plt.legend()
    plt.show()

