# -- coding utf-8 --
# Time 172019 216 PM
# Author Guanlin Chen


import math as m
import copy as cp

class Option
    def __init__(self, T, K, kind='call', geo='European')
        self.K = K
        self.T = T
        self.putcall = kind
        self.geo = geo

class Underlying
    def __init__(self, sigma, name)
        self.sigma = sigma
        self.name = name

class Environment
    def __init__(self, r) self.r = r

class Node
    def __init__(self, thetime, theID, tree)
        self.t = thetime
        self.i = theID
        self.tree = tree

    def grow(self, S0)
        up = self.tree.u
        down = self.tree.d
        if self.t == 0
            self.S = S0
        elif self.i  self.t
            self.S = self.tree.zones[self.t - 1].nodes[self.i].upprice
        else
            self.S = self.tree.zones[self.t - 1].nodes[self.i - 1].downprice
        self.upprice = self.S  up
        self.downprice = self.S  down

    def getCF(self, option)
        if option.putcall == 'call'
            self.intrinsic = max(0, self.S - option.K)
        elif option.putcall == 'put'
            self.intrinsic = max(0, option.K - self.S)
        else
            print('Unknown option type. Quitting.')
            exit()
        if self.t == self.tree.N - 1 self.opt = self.intrinsic

    def discount(self, option, env)
        p = self.tree.p
        omp = self.tree.omp
        try
            upopt = self.tree.zones[self.t + 1].nodes[self.i].opt
        except
            print(self.t + 1, self.i)
        downopt = self.tree.zones[self.t + 1].nodes[self.i + 1].opt
        discounted = (upopt  p + downopt  omp)  m.exp(-env.r  self.tree.dt)
        if option.geo != 'American' and option.geo != 'European'
            response = ''
            while response is not 'American' and response is not 'European'
                response = input(Valid option geography can be only 'Eurpoean' or 'American'. Please enter one of these, or enter 'quit' to quit)
                if response == 'quit' or response == 'Quit' or response == 'QUIT' exit()
            option.geo = response
        if option.geo == 'American'
            self.opt = max(discounted, self.intrinsic)
        elif option.geo == 'European'
            self.opt = discounted

class Tree
    def __init__(self, N)
        self.N = N
        self.zones = []
        for t in range(self.N) self.zones.append(Timezone(t, self))

    def grow(self, S0)
        for izone in self.zones izone.grow(S0)

    def getCF(self, option)
        for az in self.zones az.getCF(option)

    def discount(self, option, env)
        rzones = cp.copy(self.zones[-1])
        rzones.reverse()
        for az in rzones az.discount(option, env)

    def price(self, option, und, env, S0)
        self.dt = option.T  self.N
        self.u = m.exp(und.sigma  m.sqrt(self.dt))
        self.d = 1  self.u
        self.p = (m.exp(env.r  self.dt) - self.d)  (self.u - self.d)
        self.omp = 1 - self.p
        self.grow(S0)
        self.getCF(option)
        self.discount(option, env)
        return (self.zones[0].nodes[0].opt)

class Timezone
    def __init__(self, t, tree)
        self.t = t
        self.n = t + 1  # for this simple tree.
        self.nodes = []
        for i in range(self.n) self.nodes.append(Node(t, i, tree))

    def grow(self, S0)
        for inode in self.nodes inode.grow(S0)

    def getCF(self, option)
        for inode in self.nodes inode.getCF(option)

    def discount(self, option, env)
        for inode in self.nodes inode.discount(option, env)

class Position
    def __init__(self, n, asset)
        self.asset = asset
        self.n = n

class Strategy
    def price(self, tree, stock, env, S0)
        price = 0
        for apos in self.positions
            nshares = apos.n
            option = apos.asset
            opt_price = tree.price(option, stock, env, S0)
            price = price + nshares  opt_price
        return (price)

class Stra__le(Strategy)
    def __init__(self, T, geo='European')
        self.npos = 2
        opt1 = Option(T, None, kind='call', geo=geo)
        opt2 = Option(T, None, kind='put', geo=geo)
        pos1 = Position(1, opt1)
        pos2 = Position(1, opt2)
        self.positions = [pos1, pos2]


class Straddle(Stra__le)
    def setstrikes(self, K1, K2=None)
        self.positions[0].asset.K = K1
        self.positions[1].asset.K = K1

class Strangle(Stra__le)
    def setstrikes(self, K1, K2)
        self.positions[0].asset.K = K1
        self.positions[1].asset.K = K2

stock1 = Underlying(0.2, 'IBM')
env1 = Environment(0.05)

tree1 = Tree(200)
str1a = Straddle(T=0.75, geo=American)
str2a = Strangle(T=0.75, geo='American')
str1a.setstrikes(100)
str2a.setstrikes(100, 105)
print(str1a.price(tree1, stock1, env1, 95), str2a.price(tree1, stock1, env1, 95))