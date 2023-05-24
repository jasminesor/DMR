# coding=utf-8
# @Time : 2021/6/18 17:13
# @Author: wildpig
# @File : performance.py
# @Software: PyCharm
import logging
import os.path
import argparse
import pandas as pd
import algos
from algos.dmr import DMR
from algos.dmr import DMR as DMRUBAH
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import algos.EGtest as EGroup

# load data using tools module
# we would like to see algos progress
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
mpl.rcParams['figure.figsize'] = (16, 8)  # increase the size of graphs
mpl.rcParams['legend.fontsize'] = 12
mpl.rcParams['lines.linewidth'] = 1


def olps_stats(df):
    for name, r in df.results.iteritems():
        df.loc[name, 'sharpe'] = r.sharpe
        df.loc[name, 'information'] = r.information
        df.loc[name, 'alpha'] = r.alpha_beta()[0] * 100  # '%'
        df.loc[name, 'beta'] = r.alpha_beta()[1]
        df.loc[name, 'annualized_return'] = r.annualized_return * 100  # '%'
        df.loc[name, 'annualized_volatility'] = r.annualized_volatility * 100  # '%'
        df.loc[name, 'drawdown_period'] = r.drawdown_period
        df.loc[name, 'max_drawdown'] = r.max_drawdown * 100  # '%'
        df.loc[name, 'annual_turnover'] = r.turnover
        df.loc[name, 'total_wealth'] = r.total_wealth
        df.loc[name, 'mean_excess_return'] = r.mean_excess_return
        df.loc[name, 'calmar'] = r.calmar
        df.loc[name, 'run_time'] = r.run_time
    return df


def rrr(Names, price_data):
    olps_algos = [
        algos.BAH(),  #
        algos.UP(),  #
        algos.EG(),  #
        EGroup.EGS(),
        EGroup.WAEG(data=price_data),
        EGroup.MAEG(data=price_data),
        DMRUBAH(window=4, alpha=1000, agents_num=10, inits='mean'),
        DMR(window=4, alpha=1000, agents_num=10, inits='random')
    ]

    # put all the algos in a dataframe
    algo_names = [a.__class__.__name__ for a in olps_algos]
    algo_names[algo_names.index("DMR")] = "DMR(UBAH)"

    # name list of factor need
    algo_data = ['algo', 'results', 'sharpe', 'information',
                 'alpha', 'beta', 'annualized_return', 'annualized_volatility', 'drawdown_period',
                 'max_drawdown', 'annual_turnover', 'total_wealth', 'mean_excess_return', 'calmar', 'run_time']

    # extract all the performance factor, put it in dataframe "olps_train"
    metrics = algo_data[2:]
    olps_train = pd.DataFrame(index=algo_names, columns=algo_data)
    olps_train.algo = olps_algos

    # run all algos - this takes more than a minute
    for name, alg in zip(olps_train.index, olps_train.algo):
        olps_train.loc[name, 'results'] = alg.run(price_data)

    for k, r in olps_train.results.iteritems():
        r.fee = 0.0

    # we need 13 colors for the plot
    # n_lines = 8
    # color_idx = np.linspace(0, 1, n_lines)

    # plt.cla()
    plt.figure()
    for i in range(len(olps_algos)):
        if i > 6:
            a = 'dashdot'
        else:
            a = '-'
        plt.plot(olps_train.results[i].equity[-100:], label=olps_train.index[i], linestyle=a)
    plt.xlabel('Time', fontsize=20, fontname="Times New Roman")
    plt.ylabel('Total wealth', fontsize=20, fontname="Times New Roman")
    plt.yscale('log')
    plt.legend(loc='upper left', prop={"family": "Times New Roman", 'size': 20}, ncol=4)
    plt.title(Names, fontsize=20, fontname="Times New Roman")
    # plt.show()
    plt.savefig(f'{path}\\{Names}_cw_compare.jpg',
                bbox_inches='tight', pad_inches=0.05, dpi=700)
    # .eps files may cause bug in python now, this is a original problem in python
    # plt.savefig(f'{path}/{Names}_cw_compare.eps', format='eps',
    #             bbox_inches='tight', pad_inches=0.05, dpi=700)
    plt.close()

    # ****************feeling good for the above code, now we go ahead************************
    # collect all results of methods
    olps_stats(olps_train)
    stat_result = olps_train[metrics]
    stat_result.to_excel(f'{path}\\{Names}\\{Names}_performance.xlsx')

    # discuss the transaction cost
    fee_list = np.arange(0, 0.0031, 0.0001)
    fee_result = pd.DataFrame(columns=fee_list, index=stat_result.index)

    for fee in fee_list:
        for k, r in olps_train.results.iteritems():
            r.fee = fee

        olps_stats(olps_train)
        stat_result2 = olps_train[metrics]
        fee_result.loc[:, fee] = stat_result2.total_wealth

    fee_result.to_excel(f'{path}\\{Names}\\{Names}_fee.xlsx')

    # draw
    plt.figure()
    for i in range(fee_result.shape[0]):
        x = fee_list * 100
        if i > 6:
            a = 'dashdot'
        else:
            a = '-'
        plt.plot(x, fee_result.iloc[i, :].values, label=fee_result.index[i], linestyle=a, marker='*')
    plt.xlabel('Transaction cost(%)', fontsize=20, fontname="Times New Roman")
    plt.ylabel('Total wealth', fontsize=20, fontname="Times New Roman")
    plt.title(Names, fontsize=20, fontname="Times New Roman")
    plt.legend(loc='upper left', prop={"family": "Times New Roman", 'size': 20}, ncol=4)
    # plt.show()
    plt.savefig(f'{path}\\{Names}_cw_transaction_cost.jpg',
                bbox_inches='tight', pad_inches=0.05, dpi=700)
    # plt.savefig(f'{path}/{Names}_cw_transaction_cost.eps', format='eps',
    #             bbox_inches='tight', pad_inches=0.05, dpi=700)
    plt.close()
    # plt.clf()
    # bingo = False


if __name__ == '__main__':
    """
    this .py will calculate all the strategy performance in each dataset(Name)
    the result was output by folders which names by dataset name
    """
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

    # save place of result
    path = f"{abs_path_gf}\\result\\performance"
    for Names in Name:
        # create the folder if not exist
        os.makedirs(f"{path}\\{Names}", exist_ok=True)
        data = pd.read_excel(f'{abs_path_gf}\\data\\{Names}.xlsx')

        if 'date' in data.columns:
            del data['date']

        print(f'Now we calculate the result of dataset {Names}.')
        # bingo = True
        rrr(Names=Names, price_data=data)
        print(f'The result of dataset {Names} is done!')
        print("===" * 20)
    print(f'The result of all dataset saved! You can find it in "{path}"!')
