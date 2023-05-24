# coding=utf-8
# @Time : 2021/8/2 19:34
# @Author: wildpig
# @File : heatmaps.py
# @Software: PyCharm

import pandas as pd
from algos.dmr import DMR as DMRUBAH
import matplotlib as mpl
import matplotlib.pyplot as plt
import logging
import seaborn as sns
import os
import argparse


if __name__ == '__main__':
    # load data using tools module
    # we would like to see algos progress
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    mpl.rcParams['figure.figsize'] = (16, 8)  # increase the size of graphs
    mpl.rcParams['legend.fontsize'] = 12
    mpl.rcParams['lines.linewidth'] = 1
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
    # set parameters
    n = [1, 5, 7, 10, 15, 17, 20, 23]
    alpha_k = [1, 10, 100, 500, 1000, 5000, 10000, 20000]
    path = f"{abs_path_gf}\\result\\heatmaps"
    for names in Name:
        # 释放内存
        df = 0
        list_result = 0
        # 如果文件夹不存在就直接创建
        os.makedirs(f"{path}\\{names}", exist_ok=True)
        data = pd.read_excel(f'{abs_path_gf}\\data\\{names}.xlsx')
        if 'date' in data.columns:
            del data['date']

        list_result = DMRUBAH.run_combination(data, alpha=alpha_k, agents_num=n)
        # a bit hacky way to parse names into dictionary... I'm not proud of myself
        df = [eval(f"dict({name}, wealth={result.total_wealth})") for result, name in zip(list_result, list_result.names)]

        df = pd.DataFrame(df).pivot('alpha', 'agents_num', 'wealth').sort_index(ascending=False)
        # 导出热力图的点数据
        df.to_excel(f"{path}\\{names}_heatmap.xlsx", index=True)
        print('Heat maps is done! Now drawing the figure!')
        plt.figure(1)
        sns.heatmap(data=df, cmap=sns.cubehelix_palette(as_cmap=True), linewidths=0.1, linecolor='red')
        plt.title(f"Sentiments Heatmap for {names}.", fontname="Times New Roman")
        plt.xlabel(r"Machine number $n$", fontsize=15, fontname="Times New Roman")
        plt.ylabel(r'Step size $\alpha_k$', fontsize=15, fontname="Times New Roman")
        # 保存热力图
        plt.savefig(f'{path}\\{names}_heatmap.jpg',
                    bbox_inches='tight', pad_inches=0.05, dpi=700)
        plt.close(1)
        print("===" * 20)
        print(f"The heat map of No.{Name.index(names) + 1}/{len(Name)} dataset *{names}* is done!")
    print(f"All the heat maps are saved! You can find it in '{path}'!")
