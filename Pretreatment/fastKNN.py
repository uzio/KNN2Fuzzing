#!/usr/local/bin/python
# encoding: utf-8

import os
import csv
import operator
import pandas as pd
import numpy as np
from numpy.linalg import norm


def classify(vecX, dataSet, labels, k = 5):
    '''
    分类器

    参数：
    - vecX: 用于分类的输入向量
    - dataset: 输入的训练样本集
    - labels: 样本数据的类标签向量
    - k: 用于选择最近邻的数目
    '''
    # 获取样本数据数量
    dataSetSize = dataSet.shape[0]

    # 输入向量按样本集大小沿y轴复制，生成矩阵
    features = np.tile(vecX, (dataSetSize, 1))

    # 矩阵运算，计算样本数据矩阵与测试数据矩阵的点积
    normF = norm(features,axis=1).reshape(features.shape[0],1)
    normD = norm(dataSet,axis=1).reshape(1,dataSet.shape[0])
    end_norm = np.dot(normF,normD)

    # 计算余弦相似度与余弦距离
    similarity = np.dot(features, dataSet.T)/(end_norm+1e-32) # 添加偏差值处理除0问题
    cosDistances =1 - similarity

    # 按照距离从低到高排序
    sortedDistIndicies = cosDistances.argsort()[0]
    # 依次取出最近的样本数据
    classCount = {}
    for i in range(k):
        voteIlabel = labels[sortedDistIndicies[i]]  # 记录该样本数据所属的类别
        classCount[voteIlabel] = classCount.get(voteIlabel, 0) + 1 # 记录出现频数


    # 对类别出现的频次进行排序，从高到低
    sortedClassCount = sorted(
        classCount.items(), key=operator.itemgetter(1), reverse=True)

    # 返回出现频次最高的类别
    return sortedClassCount[0][0]



