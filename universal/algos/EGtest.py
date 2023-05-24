# -*- coding: utf-8 -*-
# @Time : 2022/2/21 16:57
# @Author : WILDPIG
# @File : EGtest.py
# @Software: PyCharm

import numpy as np
from universal.algo import Algo
from universal.algo import tools
from universal.algos.eg import EG
from universal import algos


class EGS(Algo):
    """
    EGS--考虑边信息的指数梯度策略(杨兴雨2019)《系统工程理论与实践》
    """
    def __init__(self, eta=0.05):
        """
        :param: eta: Learning rate. Controls volatility of weights.
        """
        super(EGS, self).__init__()
        self.eta = eta
        # True represent history.mean <= 1, False represent history.mean > 1
        self.side = dict(zip([True, False], [0, 1]))

    def init_weights(self, columns):
        m = len(columns)
        return np.ones(m) / m

    def step(self, x, last_b, history):
        self.side[history.iloc[-1].mean() > 1] = history.iloc[-1]
        b = self.side[history.iloc[-1].mean() > 1] * np.exp(self.eta * x / sum(x * self.side[history.iloc[-1].mean() > 1]))
        return b / sum(b)


class WAEG(Algo):
    """
    WAEG-弱集成指数梯度-离散(2019)《Computational Economics》Q4
    CAEG-弱集成指数梯度-连续(2020)《Journal of the Operational Research Society》Q4
    """
    def __init__(self, eta=0.05, etas=np.arange(0.01, 0.21, 0.01).round(2).tolist(), data=1):
        """
        :param: eta: Learning rate. Controls volatility of weights.
        """
        super(WAEG, self).__init__()
        self.eta = eta
        self.etas = etas
        self.data = data
        self.expert = dict(zip(self.etas, [EG(eta=x).run(self.data) for x in self.etas]))

    def init_weights(self, columns):
        m = len(columns)
        return np.ones(m) / m

    def step(self, x, last_b, history):
        b = 0
        s = 0
        for key in self.expert.keys():
            s_exp = self.expert[key].equity.loc[history.index[-1]]**(1 / np.sqrt(history.index[-1] + 1))
            b = b + self.expert[key].weights.loc[history.index[-1]] * s_exp
            s = s + s_exp
        return b / s


class MAEG(Algo):
    """
    MAEG--滑动窗口自适应EG策略(杨兴雨2021)《Journal of Combinatorial Optimization》Q4
    """
    def __init__(self, etas=np.arange(0.01, 0.21, 0.01).round(2).tolist(), data=1):
        """
        :param: eta: Learning rate. Controls volatility of weights.
        """
        super(MAEG, self).__init__(min_history=30)
        self.etas = etas
        self.data = data
        self.expert = dict(zip(self.etas, [EG(eta=x).run(self.data) for x in self.etas]))
        self.s = [0.01, 0]

    def init_weights(self, columns):
        m = len(columns)
        return np.ones(m) / m

    def step(self, x, last_b, history):
        for key in self.expert.keys():
            temp = self.expert[key].equity.iloc[history.index[-30:]].sum()
            if self.s[1] < temp:
                self.s[0] = key
                self.s[1] = temp
        b = last_b * np.exp(self.s[0] * x / sum(x * last_b))
        return b / sum(b)


class OEA(Algo):
    """
    OEA-在线EG策略(2020)《Optimization and Engineering》Q4
    """
    def __init__(self, data=1):
        """
        :param: eta: Learning rate. Controls volatility of weights.
        """
        super(OEA, self).__init__()
        self.data = data.copy()
        self.expert = [algos.UP().run(self.data), algos.ONS().run(self.data)]

    def init_weights(self, columns):
        m = len(columns)
        return np.ones(m) / m

    def step(self, x, last_b, history):
        b = 0
        s = 0
        for expert in self.expert:
            s_exp = expert.equity.loc[history.index[-1]]**(1 / np.sqrt(history.index[-1] + 1))
            b = b + expert.weights.loc[history.index[-1]] * s_exp
            s = s + s_exp
        return b / s


class CWOGD(Algo):
    """
    CW-OGD-组合权重在线梯度下降算法(2021)《Knowledge-Based Systems》Q2
    """
    def __init__(self, H=0.5, gamma=0.1):
        """
        :param: eta: Learning rate. Controls volatility of weights.
        """
        super(CWOGD, self).__init__()
        self.k = None
        self.eta = 1 / H
        self.gamma = gamma

    def init_weights(self, columns):
        m = len(columns)
        self.k = np.ones(m) / m
        return np.ones(m) / m

    def step(self, x, last_b, history):
        self.k = self.k - self.eta * (
                2 * self.gamma - (1 / history.iloc[-1])
        )
        b = tools.simplex_proj(self.k)
        return b * history.iloc[-1]


if __name__ == '__main__':
    data = tools.dataset('djia')
    etas = [0.01, 0.02, 0.03]
    results = MAEG(data=data).run(data)
    results.plot(weights=False, assets=False)
    print('WO')
    # tools.quickrun(EGTEST(eta=0.5), data)
