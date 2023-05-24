# coding=utf-8
# @Time : 2023/5/23 20:34
# @Author: wildpig
# @File : RunMe.py
# @Software: PyCharm
import os
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # # strategies name: default is all strategies, you can also choose single strategy
    # parser.add_argument("--s", type=str, default="all",
    #                     help=r"strategies name: default is 'all', means all strategies, "
    #                          r"you can also choose single strategy, for example: --s='BAH' means bah strategy")
    # result class: performance, heatmaps, heatmaps_alpha.
    parser.add_argument('--r', type=str, default="performance",
                        help=r"result class: performance, heatmaps, heatmaps_alpha. "
                             r"for example: --r='performance' will calculate the performance of the chased strategies.")
    # dataset structural: "all" for all dataset in "./data", "names" for "names.xlsx" in "./data"
    parser.add_argument('--d', type=str, default="all",
                        help=r"dataset: run strategies in the dataset you select. default is 'all'."
                             r"for example: --d='name' will run the strategies in 'name.xlsx', "
                             r"--d='name1,name2' will run strategies in 'name1,xlsx' and 'name2.xlsx'. "
                             r"Attention: the .xlsx files must in './data' folder before you run it!!")
    args = parser.parse_args()
    datalist = os.listdir("./data/")
    judge = [x.split(".")[1]=="xlsx" for x in datalist]
    print("==="*20)
    print("Thank you for your comment to improve our work! Now let us show the result for you!")
    print("==="*20)
    print(f"Running {args.r}...")
    if False in judge:
        print("***" * 20)
        print("Error: dataset files must be a '.xlsx' file, please check it and rerun!")
        print("***" * 20)
        sys.exit(1)
    else:
        if args.d == "all":
            print(f"Dataset chose: {[x.split('.')[0] for x in datalist]}")
        else:
            print(f"Dataset chose: {args.d.replace(' ', '').split(',')}")
        print("===" * 20)
        os.system(f"python ./universal/{args.r}.py --d={args.d}")
