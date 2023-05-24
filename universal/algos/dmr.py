# -*- coding:utf-8 -*-
# @Time : 2023/05/12 17:28
# @Author : wildpig
# @File : dmr.py
# @Software: PyCharm


import numpy as np
from universal.algo import Algo
from universal.algo import tools
import pandas as pd
import networkx as nx


def double_map(Orign):
    # input should be a pd.DataFrame
    lam = max(Orign.sum(axis=0).max(), Orign.sum(axis=1).max())
    r = len(Orign) * lam - Orign.sum().sum()
    DM = Orign.copy()
    for x in Orign.columns:
        for y in Orign.columns:
            DM.loc[x][y] = Orign.loc[x][y] + (lam - Orign.loc[x].sum()) * (lam - Orign[y].sum()) / r
    return DM / lam


class DMR(Algo):
    """ Distributed Mean Reversion Strategy for On-Line Portfolio Selection Problems

    """
    PRICE_TYPE = 'ratio'
    REPLACE_MISSING = True

    def __init__(self, window=5, alpha=1000, agents_num=10, inits='mean'):
        """
        the explain of param
        :param window: Lookback window for build the communication network
        :param alpha: decent rate
        :param method: the method of build a correlated network, default is 'cov', 'kendall', 'dbs', 'covers'
        :param agents_num: the agent names, input should be a list
        :param inits: the method of the initial weights, 'mean' means the ubah for initial weights
        """

        super(DMR, self).__init__(min_history=window)

        # # input check
        # # a self property is used to save all weight of agent
        self.inits = inits
        self.window = window
        self.alpha = alpha
        # 建立一列空权重list/dataframe存储当前时刻的智能体的权重
        self.agents = [x + 1 for x in range(agents_num)]
        # 空值字典存放每一个智能体每期的权重, 这里以后可以想想办法优化一下速度
        self.weight_dict = dict(zip(self.agents,
                                    [[] for x in self.agents]))

    # init_weights of the average agents starts
    def init_weights(self, columns):
        # 还是用随机的初始权重
        if self.inits == 'random':
            init = 0
            # np.random.seed(1)
            for key in self.weight_dict.keys():
                init_w = np.random.random(len(columns))
                self.weight_dict[key].append(init_w / init_w.sum())
                init = init + init_w / init_w.sum()
            return init / init.sum()
        else:
            for key in self.weight_dict.keys():
                self.weight_dict[key].append(np.ones(len(columns)) / len(columns))
            return np.ones(len(columns)) / len(columns)

    def step(self, x, last_b, history):
        #  按照指定的专家选择系数选取股票作为后续的专家
        if history.index.max() == self.window:
            # calculate adjacency matrix【get the experts name】
            Adj = history.iloc[-self.window:].corr(method='pearson')
            # 将非负值设定为有边连接，按行归一化，m维方阵
            Adj[Adj < 0] = 0
            # Adj = Adj.div(Adj.sum(axis=1), axis=0)
            g = nx.from_numpy_matrix(Adj.to_numpy(), create_using=nx.DiGraph())
            nodes_dict = dict(zip(list(g.nodes), Adj.columns.to_list()))
            g = nx.relabel_nodes(g, nodes_dict)
            # 排序-降序
            ord = sorted(nx.degree_centrality(g).items(), key=lambda x: x[1], reverse=True)
            # 聚类信息中的前n个的名称拿出来啦，此时agents的名称已经被替换为了选出来的stock名称了
            self.agents = list(dict(ord).keys())[0:len(self.agents)]
            for key, y in zip(list(self.weight_dict.keys()), self.agents):
                self.weight_dict[y] = self.weight_dict.pop(key)

            Communication = history[self.agents].iloc[-self.window:].corr(method='pearson')
            Communication[Communication < 0] = 0
            Communication = double_map(Communication)
            Communication.columns, Communication.index = self.agents, self.agents
        else:
            Communication = history[self.agents].iloc[-self.window:].corr(method='pearson')
            Communication[Communication < 0] = 0
            Communication = double_map(Communication)
            Communication.columns, Communication.index = self.agents, self.agents

        # extract the agents weight of previous period, mn-dimension matrix
        agent_last_weight = pd.DataFrame(columns=history.columns, index=self.agents)
        for agn in self.agents:
            agent_last_weight.loc[agn] = self.weight_dict[agn][-1]
        b = self.update(x, Communication, agent_last_weight, history.index.max())
        return b

    def update(self, x, Adjs, last_weights, num):
        """ Update portfolio weights, the returned weights should be the average of agent's weights

        """
        # 传进来的权重是所有智能体的权重进入下面的更新，保存到self.weight_dict里，但最后返回的是平均的权重
        # collect all agents weight using variable "last_b"
        last_b = 0
        # 计算每一个agnet的权重，均值保存到b中
        for agns in self.agents:
            # 综合智能体agns的邻居的权重
            agns_wei = last_weights.mul(Adjs.loc[agns], axis=0).sum()
            agns_wei = agns_wei + (1 / (num + self.alpha)) * (x / np.dot(x, agns_wei)) * (1 / len(Adjs.columns))
            # 下降后投影
            agns_wei = tools.simplex_proj(agns_wei)
            # 下降后投影，但是可卖空
            # agns_wei = avaiable_proj(agns_wei)
            self.weight_dict[agns].append(agns_wei.to_numpy())
            last_b = last_b + agns_wei
        # average all the agents weights as the strategy
        return last_b / len(Adjs.columns)


def avaiable_proj(y):
    t = 1 - np.sum(y)
    return y + t / len(y)


if __name__ == '__main__':
    tools.quickrun(DMR())
