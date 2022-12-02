import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from sklearn.neighbors import KNeighborsClassifier
from numpy import *
from QA_ReuseWater_KG import Data_Prepare

'''
使用KNN原始算法和用水质距离改进的KNN算法，输出分类结果
'''

class KNN_Class:
    # def __init__(self):
    #     DataP = Data_Prepare.DataPrepare()
    #     # 输入数据，data_dict是工艺代码与工艺流程的字典格式为{1:[工艺流程1],2:[工艺流程2],……}
    #     # data_origin格式为[[水质数据+工艺流程代号]. [], [] ……]
    #     # 水质数据顺序： quantity、runtime、recovery、COD_in、CI_in、Hardness_in、ss_in'、
    #     #               COD_out、CI_out、Hardness_out、ss_out、COD_emi、CI_emi、Hardness_emi、ss_emi、工艺代号,项目id
    #     self.data_origin, self.data_dict = DataP.Data4ClassifierTree()
    #     print(self.data_origin)
    #     print(self.data_dict)

    '''
    原始KNN分类结果
    '''
    def KNN_original(self,data_test,data_train):
        DataP = Data_Prepare.DataPrepare()
        self.data_origin, self.data_dict = DataP.Data4ClassifierTree()
        quantity = data_test[0]
        runtime = data_test[1]
        recovery = data_test[2]

        in_data = data_test[3:7]
        out_data = data_test[7:11]
        emi_data = data_test[11:15]

        data = data_train
        Xtf0 = in_data + out_data + emi_data
        Xtf = np.array(Xtf0).reshape(1, -1)
        Xf0 = []
        yf = []
        for i in data:
            Xfi = i[3:15] # 数据列
            yfi = i[16]   # lable列
            Xf0.append(Xfi)
            yf.append(yfi)
        Xf = np.array(Xf0).astype(np.float64).tolist()
        # 进行分类
        knnf = KNeighborsClassifier(n_neighbors=3)
        knnf.fit(Xf, yf)
        resultf = knnf.predict(Xtf)
        probf = knnf.predict_proba(Xtf)
        print('原始KNN各类型的分类可能性：', probf,'\n')
        print('原始KNN各类型的分类结果：', resultf, '\n')
        return resultf

    '''
    用水质距离改进后分类结果
    '''
    def KNN_wd(self, data_test,data_train):
        DataP = Data_Prepare.DataPrepare()
        self.data_origin, self.data_dict = DataP.Data4ClassifierTree()
        quantity = data_test[0]
        runtime = data_test[1]
        recovery = data_test[2]
        in_data = data_test[3:7]
        out_data = data_test[7:11]
        emi_data = data_test[11:15]

        data = data_train

        Xtf00 = in_data + out_data + emi_data
        '''给定COD、CI、Hardness、ss的基础值COD=60 CI=10000 Hardness=450 SS=5（***这个需要调试***）'''
        base_value = [50, 1000, 100, 5]
        base_value_1 = base_value+base_value+base_value
        # 计算归一化数值
        Xtf0 = list(map(lambda x: x[0] / x[1], zip(Xtf00, base_value_1)))
        Xtf = np.array(Xtf0).reshape(1, -1)
        Xf0 = []
        yf = []
        for i in data:
            Xfi0 = i[3:15]  # 数据列
            # 计算归一化数值
            Xfi = list(map(lambda x: x[0] / x[1], zip(Xfi0, base_value_1)))
            yfi = i[16]  # lable列
            Xf0.append(Xfi)
            yf.append(yfi)
        Xf = np.array(Xf0).astype(np.float64).tolist()
        # 进行分类
        knnf = KNeighborsClassifier(n_neighbors=3)
        knnf.fit(Xf, yf)
        resultf = knnf.predict(Xtf)
        probf = knnf.predict_proba(Xtf)
        print('水质改进后KNN各类型的分类可能性：', probf, '\n')
        print('水质改进后KNN各类型的分类结果：', resultf, '\n')
        return resultf

if __name__ == '__main__':
    handler = KNN_Class()

    '''
    输入需求数据
    后期使用验证集数据
    '''
    DataP = Data_Prepare.DataPrepare()
    data_origin, data_dict = DataP.Data4ClassifierTree()
    train = []
    for j in data_origin:
        train.append(j)
    test = [5000.0, 24.0, 0.67, 60.0, 6000.0, 500.0, 20.0, 5.0, 200.0, 50.0, 0.0, 182.0, 18182.0, 1515.0, 0.5, None, 1, 'MX-01']
    a=handler.KNN_original(test, train)
    print('_original_'*20)
    print(a)
    b = handler.KNN_wd(test, train)
    print('_WD_wd_' * 20)
    print(b)
