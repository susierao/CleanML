# define the domain of error type 
from .clean_method import *

# details of each error type
missing_values = {
    "name": "missing_values",
    "clean_methods": {"delete": MVCleaner("delete"),
                      "impute_mean_mode": MVCleaner("impute", num="mean", cat="mode"),
                      "impute_mean_dummy": MVCleaner("impute", num="mean", cat="dummy"),
                      "impute_median_mode": MVCleaner("impute", num="median", cat="mode"),
                      "impute_median_dummy": MVCleaner("impute", num="median", cat="dummy"),
                      "impute_mode_mode": MVCleaner("impute", num="mode", cat="mode"),
                      "impute_mode_dummy": MVCleaner("impute", num="mode", cat="dummy")
                    }
}

outliers = {
    "name": "outliers",
<<<<<<< HEAD
    "clean_methods": {"SD_impute_mean_dummy": OutlierCleaner(detect_method="SD", repairer=MVCleaner("impute", num="mean", cat="dummy")),
                      "SD_impute_mode_dummy": OutlierCleaner(detect_method="SD", repairer=MVCleaner("impute", num="mode", cat="dummy")),
                      "SD_impute_median_dummy": OutlierCleaner(detect_method="SD", repairer=MVCleaner("impute", num="median", cat="dummy")),
                      "SD_impute_delete": OutlierCleaner(detect_method="SD", repairer=MVCleaner("delete")),
                      "IQR_impute_mean_dummy": OutlierCleaner(detect_method="IQR", repairer=MVCleaner("impute", num="mean", cat="dummy")),
                      "IQR_impute_mode_dummy": OutlierCleaner(detect_method="IQR", repairer=MVCleaner("impute", num="mode", cat="dummy")),
                      "IQR_impute_median_dummy": OutlierCleaner(detect_method="IQR", repairer=MVCleaner("impute", num="median", cat="dummy")),
                      "IQR_impute_delete": OutlierCleaner(detect_method="IQR", repairer=MVCleaner("delete")),
                      "IF_impute_mean_dummy": OutlierCleaner(detect_method="IF", repairer=MVCleaner("impute", num="mean", cat="dummy")),
                      "IF_impute_mode_dummy": OutlierCleaner(detect_method="IF", repairer=MVCleaner("impute", num="mode", cat="dummy")),
                      "IF_impute_median_dummy": OutlierCleaner(detect_method="IF", repairer=MVCleaner("impute", num="median", cat="dummy")),
                      "IF_impute_delete": OutlierCleaner(detect_method="IF", repairer=MVCleaner("delete"))
=======
    "clean_methods": {"clean_SD_impute_mean_dummy": OutlierCleaner(detect_method="SD", repairer=MVCleaner("impute", num="mean", cat="dummy")),
                      "clean_SD_impute_mode_dummy": OutlierCleaner(detect_method="SD", repairer=MVCleaner("impute", num="mode", cat="dummy")),
                      "clean_SD_impute_median_dummy": OutlierCleaner(detect_method="SD", repairer=MVCleaner("impute", num="median", cat="dummy")),
                      "clean_SD_delete": OutlierCleaner(detect_method="SD", repairer=MVCleaner("delete")),
                      "clean_IQR_impute_mean_dummy": OutlierCleaner(detect_method="IQR", repairer=MVCleaner("impute", num="mean", cat="dummy")),
                      "clean_IQR_impute_mode_dummy": OutlierCleaner(detect_method="IQR", repairer=MVCleaner("impute", num="mode", cat="dummy")),
                      "clean_IQR_impute_median_dummy": OutlierCleaner(detect_method="IQR", repairer=MVCleaner("impute", num="median", cat="dummy")),
                      "clean_IQR_delete": OutlierCleaner(detect_method="IQR", repairer=MVCleaner("delete")),
                      "clean_IF_impute_mean_dummy": OutlierCleaner(detect_method="IF", repairer=MVCleaner("impute", num="mean", cat="dummy")),
                      "clean_IF_impute_mode_dummy": OutlierCleaner(detect_method="IF", repairer=MVCleaner("impute", num="mode", cat="dummy")),
                      "clean_IF_impute_median_dummy": OutlierCleaner(detect_method="IF", repairer=MVCleaner("impute", num="median", cat="dummy")),
                      "clean_IF_delete": OutlierCleaner(detect_method="IF", repairer=MVCleaner("delete"))
>>>>>>> e15611936ff0ca40875dd800821185b6e2bf3d02
                    }
}

mislabel = {
    "name": "mislabel",
    "clean_methods": {"clean": MislabelCleaner()}
}

duplicates = {
    "name": "duplicates",
    "clean_methods": {"clean": DuplicatesCleaner()}
}

inconsistency = {
    "name": "inconsistency",
    "clean_methods": {"clean": InconsistencyCleaner()}
}

# domain of error types
error_types = [missing_values, outliers, mislabel, inconsistency, duplicates]