# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 11:58:31 2017

@author: hankk
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split
import statsmodels.api as sm

# read and copy data
path = ".../default-of-credit-card-clients-dataset"
os.chdir(path)
data = pd.read_csv("creditCard_UCI.csv")
df = data.copy()

y = df['default payment next month']
# y = df['target']

"""
数据转换
"""
# data transform
df.EDUCATION.unique()
df.MARRIAGE.unique()

"""
df.MARRIAGE = df.MARRIAGE.map({0:'unkown', 1:1, 2:0, 3:'unkown'})
df["EDUCATION"] = df["EDUCATION"].map({0: 'unkown', 1:1, 2:2, 3:3, 4:'unkown', 
    								    5:'unkown', 6: 'unkown'})
"""

"""
单个变量woe转换后建立logistic模型
"""
"""
x_woe, woe_map, iv = _single_woe_trans(df.EDUCATION, y)

logit_instance, logit_model, logit_result, logit_result_0 = logistic_reg(x_woe, 
                                                                         y)

desc, params, evaluate, quality = logit_output(logit_instance, 
                                               logit_model, 
                                               logit_result, 
                                               logit_result_0)
"""
"""
对所有变量进行woe转换
"""

# bining continnues var
continnues = ['LIMIT_BAL', 'AGE',
              'BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3',
              'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6',
              'PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3',
              'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6', ]

dc = df[continnues]


def _tempFunc_1(dc, y, method):
    """
    temp function for data bining
    """
    new_ds = pd.DataFrame()
    for v in dc.columns:
        x = dc[v]
        bin_map = binContVar(x, y, method)
        new_x = _applyBinMap(x, bin_map)
        new_x.name = v + "_BIN"
        new_ds = pd.concat([new_ds, new_x], axis=1)
    return new_ds


new_dc = _tempFunc_1(dc, y, method=4)

# charachter var reduce catagory
characters = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']
ds = df[characters]

bin_maps_str = dict()
for var in ds.columns:
    x = ds[var]
    single_map = reduceCats(x, y, method=4)
    bin_maps[x.name] = single_map

new_PAY_0 = applyMapCats(df.PAY_0, bin_maps_str['PAY_0'])
new_PAY_3 = applyMapCats(df.PAY_3, bin_maps_str['PAY_3'])
new_PAY_4 = applyMapCats(df.PAY_4, bin_maps_str['PAY_4'])
new_PAY_5 = applyMapCats(df.PAY_5, bin_maps_str['PAY_5'])
new_PAY_6 = applyMapCats(df.PAY_6, bin_maps_str['PAY_6'])
new_PAY_2 = applyMapCats(df.PAY_2, bin_maps_str['PAY_2'])

# data combine
new_df = pd.concat([new_ds,
                    new_PAY_0,
                    new_PAY_2,
                    new_PAY_3,
                    new_PAY_4,
                    new_PAY_5,
                    new_PAY_6], axis=1)
new_df = pd.concat([new_df, df.SEX, df.EDUCATION, df.MARRIAGE], axis=1)

# WOE transform
df_woe_X, woe_maps, iv_values = woe_trans(new_df.columns, y, new_df)

varNames = df_woe_X.columns
woe_vars = varNames[varNames.str.endswith('_WOE')]
woe_df = df_woe_X[woe_vars]

"""
数据划分
"""

X_train, X_test, y_train, y_test = train_test_split(woe_df, y, test_size=0.33)

"""
模型开发
"""
logit_instance, logit_model, logit_result, logit_result_0 = logistic_reg(X_train,
                                                                         y_train,
                                                                         stepwise='BS')

desc, params, evaluate, quality = logit_output(logit_instance,
                                               logit_model,
                                               logit_result,
                                               logit_result_0)

"""
模型评价
"""
# 生成模型评价数据
prob_y_train = logit_result.predict()
X_test_metric = sm.add_constant(X_test[params.index[1:]])
prob_y_test = logit_result.predict(X_test_metric)
label_pred_test = np.where(prob_y_test > 0.5, 1, 0)

# ROC 曲线
plot_roc_curve(prob_y_test, y_test)
# KS表&KS曲线
ks_stattable, _ = ks_stats(prob_y_test, y_test)
# 提升图&lorenz曲线
lift_lorenz(prob_y_test, y_test)

plot_confusion_matrix(y_test, label_pred_test, labels=[0, 1])

"""
生成评分卡
"""
method = 4
var_list = list(params.index)
est = params['参数估计']

for v in dc.columns:
    x = dc[v]
    bin_map = binContVar(x, y, method)
    bin_maps[v] = bin_map

LIMIT_BAL_BIN_MAP = binContVar(df['LIMIT_BAL'], y, method=4)
AGE_BIN_MAP = binContVar(df['AGE'], y, method=4)
bill_amt6_bin_map = binContVar(df['BILL_AMT6'], y, method=4)

PAY_AMT1_bin_map = binContVar(df['PAY_AMT1'], y, method=4)
PAY_AMT2_bin_map = binContVar(df['PAY_AMT2'], y, method=4)
PAY_AMT5_bin_map = binContVar(df['PAY_AMT5'], y, method=4)