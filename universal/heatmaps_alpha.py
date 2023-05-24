# coding=utf-8
# @Time : 2021/5/26 22:50
# @Author: wildpig
# @File : heatmaps_alpha.py
# @Software: PyCharm

import pandas as pd
import os
import matplotlib as mpl
import logging
from algos.dmr import DMR as DMRUBAH
import argparse


if __name__ == '__main__':
    # os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    parser = argparse.ArgumentParser()
    parser.add_argument('--d', type=str, default="all",
                        help=r"dataset name: chose dataset, default is 'all'."
                             r"for example: --d='name' will select the dataset files 'name.xlsx', "
                             r"--d='name1,name2' will select the dataset files 'name1,xlsx' and 'name2.xlsx'. "
                             r"Attention: the .xlsx files must in './data' before you run it!!")
    args = parser.parse_args()
    abs_path_gf = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if args.d == 'all':
        Name = [x.replace('.xlsx', '') for x in os.listdir(f"{abs_path_gf}\\data\\")]
    else:
        Name = args.d.replace(" ", "").split(",")
    # load data using tools module
    # we would like to see algos progress
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    mpl.rcParams['figure.figsize'] = (16, 8)  # increase the size of graphs
    mpl.rcParams['legend.fontsize'] = 12
    mpl.rcParams['lines.linewidth'] = 1
    alpha_k = [1, 10, 100, 500, 1000, 5000, 10000, 20000]
    path = f"{abs_path_gf}\\result\\heatmaps_for_alpha"
    metrics = ['sharpe', 'information', 'alpha', 'beta', 'annualized_return', 'annualized_volatility',
               'drawdown_period', 'max_drawdown', 'annual_turnover', 'total_wealth', 'mean_excess_return',
               'calmar', 'run_time', 'alpha_t', 'alpha_p']
    for name in Name:
        print(f"Now running the sentiment of alpha_k in No.{Name.index(name) + 1}/{len(Name)} dataset {name}!")
        os.makedirs(f"{path}\\{name}", exist_ok=True)
        data = pd.read_excel(f'{abs_path_gf}\\data\\{name}.xlsx')
        if 'date' in data.columns:
            del data['date']

        algo_result = DMRUBAH.run_combination(data, alpha=alpha_k)
        # storage all the result
        result_name = pd.DataFrame(columns=metrics)
        for num, res in zip(alpha_k, algo_result):
            result_name.loc[num, 'sharpe'] = res.sharpe
            result_name.loc[num, 'information'] = res.information
            result_name.loc[num, 'alpha'] = res.alpha_beta()[0] * 100  # '%'
            result_name.loc[num, 'beta'] = res.alpha_beta()[1]
            result_name.loc[num, 'annualized_return'] = res.annualized_return * 100  # '%'
            result_name.loc[num, 'annualized_volatility'] = res.annualized_volatility * 100  # '%'
            result_name.loc[num, 'drawdown_period'] = res.drawdown_period
            result_name.loc[num, 'max_drawdown'] = res.max_drawdown * 100  # '%'
            result_name.loc[num, 'annual_turnover'] = res.turnover
            result_name.loc[num, 'total_wealth'] = res.total_wealth
            result_name.loc[num, 'mean_excess_return'] = res.mean_excess_return
            result_name.loc[num, 'calmar'] = res.calmar
            result_name.loc[num, 'run_time'] = res.run_time
            # t-test
            alpha_ttest = res.alpha_ttest()
            result_name.loc[num, 'alpha_t'] = alpha_ttest[0]
            result_name.loc[num, 'alpha_p'] = alpha_ttest[1]

        result_name.to_excel(f"{path}\\{name}.xlsx", encoding="utf-8_sig")
        print(f"The sentiment of alpha_k in dataset *{name}* is done!")
        print("===" * 20)
    print(f"All done! You can find it in '{path}'")
