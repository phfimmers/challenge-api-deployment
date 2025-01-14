import pandas as pd
import numpy as np
import os
from typing import List
from typing import Dict

# from pandas_profiling import ProfileReport

pd.options.display.max_rows = 20
pd.options.display.max_columns = None

"""DEFAULT VALUES SETUP"""
#FM 8/12/20 filepaths moved to models_creation.py

# for terrace and garden it will be double checked if their related boolean is True when area is 0
COLUMNS_NAN_REPLACE_WITH = {"terrace_area": 0, "garden_area": 0, "facades_number": 0}
# for outliers detection Tukey fences are used instead of percentile due to not normal distribution
OUTLIERS_METHODS = ["fence_tukey_min", "fence_tukey_max"]  # , "5%", "95%"]
# numerical categorical columns are excluded from outliers analysis
# boolean (onlt two distinct values) are excluded automatically as not being np.numeric
# columns with prevalent nan values (previously filled with zero) excluded:
# garden_area, terrace_area, land_surface, facades_number
COLUMNS_OUTLIERS_IGNORE = ["facades_number", "garden_area", "postcode", "src", "terrace_area", "land_surface",
                           "price_m_by_postcode", "latitude", "longitude"]
# during the profiling dominant values found in equipped kitchen (true, 83.7%), furnished (False, 96.3%), Open Fire (False, 93.5%)
# columns with a dominant value (inc. src and swimming pool) are excluded from duplicates check.
# related boolean columns (e.g. garden_has) are also excluded.
# region is excluded having already postcode
# building_state_agg is excluded since aggregation of different approaches from different sources.
# more info in previous project repository https://github.com/FrancescoMariottini/residential-real-estate-analysis/blob/main/README.md
COLUMNS_DUPLICATES_CHECK = ["postcode", "house_is", "property_subtype", "price", "rooms_number", "area"]
# aggregation for median price was based on related available official statistics (statbel)
# building_state_agg not available in statbel but could maybe retrieved in a different way
# e.g. distinction between old and new buildings
COLUMNS_GROUPED_BY = {"facades_number": "property_subtype"} #not neeeded by Ankita: "price":"property_subtype", "price":"region"}  "price":"building_state_agg"}
COLUMNS_TO_REPLACE = ["facades_number"]
GROUPBY_AGGREGATORS = [np.median]  # [min,max,np.mean,np.median,len]
AGGREGATOR_COLUMNS = {min: "min", max: "max", np.mean: "mean", np.median: "median", len: "len"}
#FM 7/12/20 defining allowed model subtypes
MODEL_SUBTYPES = ["APARTMENT", "HOUSE", "OTHERS"]
OTHER_PROPERTY_SUBTYPES = ["OTHER_PROPERTY", "MIXED_USE_BUILDING"]
FEATURES_MANDATORY = ["area", "rooms_number", "postcode"]
TARGET = "price"
LOG_ON_COLUMNS = ["garden_area", "terrace_area", "land_surface", "area"]
# Not used yet
REPORT_HTML_FILEPATH = os.getcwd() + "\\reports" + "\\df_before_cleaning.html"

def get_columns_with_nan(df: pd.DataFrame) -> List[str]:
    """
    Obtain columns having at least one nan
    :param df: input table
    :return columns_with_nan:
    """
    columns_with_nan = []
    for c in df.columns:
        c_na_count = df[c].isna().sum()
        if c_na_count > 0:
            columns_with_nan.append(c)
    return columns_with_nan


def describe_with_tukey_fences(df: pd.DataFrame,
                               percentiles: List[float] = [0.95, 0.94, 0.75, 0.5, 0.25, 0.06, 0.05]) -> pd.DataFrame:
    """
    Add tukey fences (for non-normal distribution) to pandas describe method for outliers detection
    :param df: input table
    :param percentiles: percentiles requested
    :return df_desc: description as dataframe including fence_tukey_min and fence_tukey_max
    """
    if 0.25 not in percentiles:
        percentiles.append(0.25)
    if 0.75 not in percentiles:
        percentiles.append(0.75)
    df_desc = df.describe(percentiles, include=np.number)
    df_index = df_desc.index.to_list()
    fence_tukey_min: List = [df_desc.loc["25%", c] - 1.5 * (df_desc.loc["75%", c] - df_desc.loc["25%", c]) for c in
                             df_desc.columns]
    fence_tukey_max: List = [df_desc.loc["75%", c] + 1.5 * (df_desc.loc["75%", c] - df_desc.loc["25%", c]) for c in
                             df_desc.columns]
    df_desc = df_desc.append(dict(zip(df_desc.columns, fence_tukey_min)), ignore_index=True)
    df_desc = df_desc.append(dict(zip(df_desc.columns, fence_tukey_max)), ignore_index=True)
    df_index.append('fence_tukey_min')
    df_index.append('fence_tukey_max')
    df_desc.index = df_index
    return df_desc


def get_outliers_index(df: pd.DataFrame, outliers_methods: List[str] = OUTLIERS_METHODS,
                       columns_outliers_ignore: List[str] = COLUMNS_OUTLIERS_IGNORE) -> pd.DataFrame:
    """
    Identify outliers in a dataframe using tukey and/or percentile fences
    :param df: input table
    :param outliers_methods: from the index of describe_with_tukey_fences() description dataframe
    :param columns_outliers_ignore: numerical columns to be ignored
    :return df_outliers: table with column, method, type, count (of outliers), % (of the rows), first outlier and index (list)
    # type is min or max
    # first outlier is the outlier closest to the accepted values
    """
    df_desc: pd.DataFrame = describe_with_tukey_fences(df)
    columns = [c for c in df_desc.columns if c not in columns_outliers_ignore]
    df_outliers = pd.DataFrame(columns=["column", "method", "type", "count", "%", "first_outlier", "index"])
    for c in columns:
        t_min, t_max, p95, p94, p06, p05 = df_desc.loc[
            ["fence_tukey_min", "fence_tukey_max", "95%", "94%", "6%", "5%"], c]
        for m in outliers_methods:
            # TBC elif (fence_tukey_max < p95) AND (p95 != p94):
            if m == "fence_tukey_min" or m == "5%":
                outliers = df.loc[df[c] < df_desc.loc[m, c], c]
                o_type = 'min'
            elif m == "fence_tukey_max" or m == "95%":
                outliers = df.loc[df[c] > df_desc.loc[m, c], c]
                o_type = 'max'
            index = outliers.index
            if len(index) > 0:
                if o_type == 'min':
                    first_outlier = max(outliers)
                elif o_type == 'max':
                    first_outlier = min(outliers)
                df_outliers = df_outliers.append({"column": c, "method": m, "type": o_type, "count": len(index),
                                                  "%": round(len(index) / len(df) * 100, 2),
                                                  "first_outlier": first_outlier,
                                                  "index": index.tolist()}, ignore_index=True)
    return df_outliers


# QA how specify list of functions in typing ?
def add_aggregated_columns(df: pd.DataFrame, group_parameters: Dict[str, str] = COLUMNS_GROUPED_BY,
                          groupby_aggregators: List = GROUPBY_AGGREGATORS,
                          columns_to_replace: List[str] = None) -> (pd.DataFrame, List[str]):
    """
    Create aggregated columns to deal with missing values and non-numerical values
    :param df: input table
    :param group_parameters: parameter and column to group for.
    :param groupby_aggregators: aggregate function to use
    :param columns_to_replace: original columns to be replaced with grouped values
    :return df: dataframe with new aggregated columns
    :return column_names: names of added aggregated columns
    """
    aggregated_column_names = []
    for key, value in group_parameters.items():
        df_grp = df.loc[:, [key, value]].dropna(axis=0).groupby(value, as_index=False)[key].agg(groupby_aggregators)
        column_names = [f"{value}_{AGGREGATOR_COLUMNS[aggregator]}_{key}" for aggregator in groupby_aggregators]
        df = df.merge(df_grp, on=value, how='left')
        aggregated_column_names += column_names
        df.rename(columns=dict(zip([AGGREGATOR_COLUMNS[aggregator] for aggregator in groupby_aggregators], column_names)), inplace=True)
    # drop at the end so order in group_parameters not important
    if columns_to_replace is not None:
        df.drop(labels=[c for c in columns_to_replace], axis=1, inplace=True)
        df.rename(columns={'property_subtype_median_facades_number': "facades_number"}, inplace=True) #24/11/20 fast fix
    return df, column_names

class DataCleaning:
    def __init__(self,
                 csv_filepath: str, #FM 8/12/20 replaced with mandatory
                 cleaned_csv_path: str = None, #FM 8/12/20 default replaced with None
                 columns_nan_replace_with: Dict[str, int] = COLUMNS_NAN_REPLACE_WITH,
                 columns_duplicates_check: List[str] = COLUMNS_DUPLICATES_CHECK,
                 columns_outliers_ignore: List[str] = COLUMNS_OUTLIERS_IGNORE,
                 outliers_methods: List[str] = OUTLIERS_METHODS,

                 property_subtype: str = None,
                 report_html_filepath: str = REPORT_HTML_FILEPATH, #future release (profiling used for preliminary analysis)
                 ):
        """
        Initialise the dataset cleaning class
        :param csv_filepath: path to the input csv file
        :param columns_nan_replace_with: columns for which nan will be replaced
        :param columns_duplicates_check: columns used as subset for checking duplicates
        :param columns_outliers_ignore: columns for which outliers won't be checked and removed
        :param outliers_methods: see get_outliers_index() method
        :param cleaned_csv_path: path to create the output csv file
        :param report_html_filepath: path to create the pandas_profiling (future release)
        :param: property_subtype: if a specific subtype have to be extracted
        :argument: df_0: original table
        :argument: df_out: modified table
        :argument: columns_with_nan: see fill_na() method
        :argument: index_removed_by_process: store removed indexes through processes
        :argument: outliers: see get_outliers() method
        """
        self.df_0: pd.DataFrame = pd.read_csv(csv_filepath)
        #FM 8/12/20 mixed used building dealt later
        # if property_subtype is None:
            #FM 8/12/2020 MIXED_USE_BUILDING removed for all cases
            # self.df_0 = self.df_0[self.df_0.property_subtype != "MIXED_USE_BUILDING"]
        if property_subtype is not None:
            self.df_0 = self.df_0[self.df_0.property_subtype == property_subtype]

        self.df_out: pd.DataFrame = self.df_0.copy(deep=True)
        self.columns_with_nan: List[str] = []
        self.index_removed_by_process: Dict[str, List] = {}
        self.outliers = pd.DataFrame(columns=["column", "method", "count", "%", "first_outlier", "index"])
        #FM 8/12/20 transformations recording, time could be added
        self.converters = pd.DataFrame(columns=["column","method","description"])

        self.columns_nan_replace_with = columns_nan_replace_with
        self.columns_duplicates_check = columns_duplicates_check
        self.columns_outliers_ignore = columns_outliers_ignore
        self.outliers_methods = outliers_methods
        self.cleaned_csv_path = cleaned_csv_path

        # not used yet
        #self.report_html_filepath = report_html_filepath

    def fill_na(self, df_before: pd.DataFrame = None,
                columns_nan_replace_with: Dict[str, int] = None,
                inplace=True) -> pd.DataFrame:
        """
        Fill na in the requested columns and return where nan where found
        :param df_before: provided table
        :param columns_nan_replace_with: columns for which to replace nan
        :param inplace: modify the dataframe inside
        :return df_out: table without nan
        """
        if df_before is None:
            df_before = self.df_out
        if columns_nan_replace_with is None:
            columns_nan_replace_with = self.columns_nan_replace_with
        df_out = df_before.fillna(columns_nan_replace_with)
        if inplace:
            self.df_out = df_out
        return df_out

    def drop_duplicates(self, df_before: pd.DataFrame = None, columns_duplicates_check: List = None,
                        inplace=True) -> (pd.DataFrame, List):
        """
        Drop duplicated based on target columns
        :param df_before: provided table
        :param columns_duplicates_check: columns subset for duplicates checking
        :param inplace: implement changes and store information into the DataCleaning class
        :return df_out: table without the duplicates
        :return index_dropped: list of indexes dropped within the process
        """
        if df_before is None:
            df_before = self.df_out
        if columns_duplicates_check is None:
            columns_duplicates_check = self.columns_duplicates_check
        df_out = df_before.drop_duplicates(subset=columns_duplicates_check)
        index_dropped = df_before.index.difference(df_out.index).tolist()
        if inplace:
            self.df_out = df_out
            self.index_removed_by_process["duplicates_removed"]: List = index_dropped
        return df_out, index_dropped

    def get_outliers(self, df: pd.DataFrame = None, columns_outliers_ignore: List = None,
                     outliers_methods: List[str] = None, inplace=True) -> pd.DataFrame:
        """
        Call get_outliers_index() method to identify outliers
        :param df: table to be analysed
        :param columns_outliers_ignore: numerical columns to be ignored for outliers detection
        :param outliers_methods: see get_outliers_index() method
        :param inplace: implement changes and store information into the DataCleaning class
        :return df_outliers: table with information on detected outlier, see get_outliers_index() method
        """
        if df is None:
            df = self.df_out
        if columns_outliers_ignore is None:
            columns_outliers_ignore = self.columns_outliers_ignore
        if outliers_methods is None:
            outliers_methods = self.outliers_methods
        df_outliers = get_outliers_index(df, outliers_methods, columns_outliers_ignore)
        if inplace:
            self.outliers = df_outliers
        return df_outliers

    def drop_outliers(self, df_before: pd.DataFrame = None, columns_outliers_ignore: List = None,
                      outliers_methods: List[str] = None, inplace=True) -> (pd.DataFrame, List):
        """
        Drop outliers as identified through the get_outliers() method
        :param df_before: provided table
        :param columns_outliers_ignore: numerical columns to be ignored for outliers detection
        :param outliers_methods: see get_outliers_index() method
        :param inplace: implement changes and store information into the DataCleaning class
        :return df_out: table without the outliers
        :return index_dropped: indexes dropped within the process
        """
        if df_before is None:
            df_before = self.df_out
        if columns_outliers_ignore is None:
            columns_outliers_ignore = self.columns_outliers_ignore
        if outliers_methods is None:
            outliers_methods = self.outliers_methods
        df_outliers = self.get_outliers(df_before, columns_outliers_ignore, outliers_methods)
        index_dropped = []
        for index, row in df_outliers.iterrows():
            count, index = df_outliers.loc[index, ["count", "index"]]
            if count > 1:
                for i in index:
                    if i not in index_dropped:
                        index_dropped.append(i)
        df_out = df_before[~df_before.index.isin(index_dropped)]
        if inplace:
            self.index_removed_by_process["outliers_removed"]: List = index_dropped
            self.df_out = df_out
        return df_out, index_dropped
    
    def preprocess_features(self, df_before: pd.DataFrame = None,
                            features: List[str] = None,
                            target: str = TARGET,
                            model_subtype: str = "OTHERS",
                            other_property_subtypes: List[str] = OTHER_PROPERTY_SUBTYPES,
                            log_on_columns: List[str] = LOG_ON_COLUMNS):
        #FM 8/12/20 future: partly to be moved to aggregated columns
        if df_before is None:
            df_before = self.df_out
        #8/12/20 adding main features if not inserted
        if features == None:
            features = df_before.columns.to_list()
            features.remove(target)
        for f in FEATURES_MANDATORY:
            if f not in features:
                features += [f]
        df_out = df_before.copy(deep=True)

        #replacing bool to avoid scikit-learn issue later
        df_out = df_out.replace(to_replace=[True, False], value=[1, 0])
        df_out = df_out.loc[:, features+["house_is"]+["property_subtype"]+[target]]

        """
        #preprocessing after database
        # FM 7/12/20 filtering dataframe before hot encoding
        # postcode_stats contains the no. of properties in each postcode
        postcode_stats = df_out['postcode'].value_counts(ascending=False)
        # Any location having less than 10 dataset points should be tagged as "9999" location.
        # This way number of categories can be reduced by huge amount.
        # Later on when we do one hot encoding, it will help us with having fewer dummy columns
        postcode_value_less_than_10 = postcode_stats[postcode_stats <= 10]
        df_out['postcode'] = df_out['postcode'].apply(lambda x: '9999' if x in postcode_value_less_than_10 else x)
        df_out['house_is'] = df_out['house_is'].apply(lambda x: "APARTMENT" if x == False else "HOUSE")
        df_out.loc[df_out['property_subtype'].isin(other_property_subtypes), "house_is"] = "OTHERS"
        if model_subtype not in MODEL_SUBTYPES:
            print(f'{model_subtype} model not found, OTHERS model used. Available models are:')
            print(",".join([m for m in MODEL_SUBTYPES]))
            model_subtype = "OTHERS"
        df_out = df_out.loc[df_out['house_is'] == model_subtype, :]
        # remove column since only one unique value
        self.converters.append({"column": "house_is", "method": "type aggregation", "description": "to use submodel"},
                               ignore_index=True)
        # keep only the features which are irrelevant as per chi - square
        features.append(target)
        df_out = df_out.loc[:, features]
        for c in log_on_columns:
            df_out[c] = df_out[c].replace(to_replace=0, value=1)
            df_out[c] = df_out[c].apply(np.log)
            self.converters.append({"column": c, "method": "log", "description": "to improve model"}, ignore_index=True)
        """


        return df_out
        

    def get_preprocessed_dataframe(self, cleaned_csv_path: str = None,
                                   features: List[str] = FEATURES_MANDATORY,
                                   model_subtype: str = "OTHERS",
                                   log_on_columns: List[str] = LOG_ON_COLUMNS) -> (pd.DataFrame, pd.DataFrame):
        """
        Wrap-up method to clean the table and provide the main outputs in one line
        :param cleaned_csv_path: output path for the csv file
        :return df_out: cleaned table
        :return df_outliers: information about the outliers
        """
        print(f"Initial dataset, shape: {self.df_0.shape}")
        # aggregation to deal with many nan in facades_number
        self.df_out, aggregated_column_names = add_aggregated_columns(self.df_out, columns_to_replace=COLUMNS_TO_REPLACE)
        self.columns_outliers_ignore += aggregated_column_names
        print(f"Aggregated parameters replacing categorical ones, shape: {self.df_out.shape}")
        self.df_out, index_dropped = self.drop_duplicates()
        #fill nan after replacing facades_number with grouping to avoid modelling issues
        self.df_out = self.fill_na(self.df_out)
        print(f"{len(index_dropped)} Dropped duplicates, shape: {self.df_out.shape}")
        df_outliers = self.get_outliers()
        #self.df_out, index_dropped = self.drop_outliers() #not dropping won't affect too much the accuracy
        #print(f"{len(index_dropped)} Dropped outliers, shape: {self.df_out.shape}")
        #8/12/2020 adding preprocessing
        self.df_out = self.preprocess_features(df_before= self.df_out,
                                                features= features, model_subtype= model_subtype,
                                               log_on_columns = log_on_columns)
        
        if cleaned_csv_path is not None:
            self.df_out.to_csv(cleaned_csv_path)
        return self.df_out, df_outliers
