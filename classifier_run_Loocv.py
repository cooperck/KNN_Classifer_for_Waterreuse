from Classifier_test import KNN_pro
from Classifier_test import KNN
from QA_ReuseWater_KG import Data_Prepare
import random
from statistics import mean

'''
本文档用于测试KNNpro与KNN两文档中算法的可靠性
输入需求数据
从Data_Prepare中提取data_origin
然后用两种方法验证可靠性：
1、留出法hold-out，训练测试7：3进行10次随机划分，结果取平均值
2、留一交叉验证法LOOCV方法进行交叉验证，即（Leave-one-out cross-validation）：
只用一个数据作为测试集，其他的数据都作为训练集，并将此步骤重复N次（N为数据集的数据数量）

最后计算准确率、精确率、召回率、F-Measure等评价指标
'''

DataP = Data_Prepare.DataPrepare()
data_origin, data_dict = DataP.Data4ClassifierTree()
print('\n','data_dict'*20)
print(data_dict,'\n')
print('\n','data_origin'*20)
print(data_origin,'\n')
# 水质数据顺序： quantity、runtime、recovery、COD_in、CI_in、Hardness_in、ss_in'、
#               COD_out、CI_out、Hardness_out、ss_out、COD_emi、CI_emi、Hardness_emi、ss_emi



'''
用LOOCV方法进行交叉验证，即（Leave-one-out cross-validation）
'''

T_num_o_all = 0 # 记录原始KNN正确数量总值
T_num_wd_all = 0 # 记录水质改进KNN正确数量总值
T_num_p_all = 0 # 记录逻辑判断与水质距离改进型KNN正确数量总值
T_num_o_ave = 0 # 记录原始KNN正确数量平均值
T_num_wd_ave = 0 # 记录水质改进KNN正确数量平均值
T_num_p_ave = 0 # 记录逻辑判断与水质距离改进型KNN正确数量平均值
code_list = list(data_dict.keys())
TP_o = {}
TP_wd = {}
TP_p = {}
FP_o = {}
FP_wd = {}
FP_p = {}
TN_o = {}
TN_wd = {}
TN_p = {}
FN_o = {}
FN_wd = {}
FN_p = {}# 给三个算法的TP、FP、TN、FN赋初使值
for i in code_list:
    TP_o[i] = TP_wd[i] = TP_p[i] = FP_o[i] = FP_wd[i] = FP_p[i] = \
    TN_o[i] = TN_wd[i] = TN_p[i] = FN_o[i] = FN_wd[i] = FN_p[i] = 0
count = 0

precision_o = {}
precision_wd = {}
precision_p = {} # 记录每个工艺的精确率，为一个字典
recall_o = {}
recall_wd = {}
recall_p = {}  # 记录每个工艺的召回率，为一个字典

precision_dict_o = {}
precision_dict_wd = {}
precision_dict_p = {} # 定义这次循环的精确率字典
recall_dict_o  = {}
recall_dict_wd = {}
recall_dict_p = {} # 定义这次循环的召回率字典
for i in code_list:
    precision_dict_o[i] = precision_dict_wd[i] = precision_dict_p[i] =\
    recall_dict_o[i] = recall_dict_wd[i] = recall_dict_p[i] = 0

T_num_o = 0   # 记录原始型正确的数量
T_num_wd = 0  # 记录水质距离改进型正确的数量
T_num_p = 0   # 记录逻辑判断与水质距离改进型正确的数量

l= len(data_origin)
for x in range(0,l):
    # 选取测试集
    train_set_h = []
    test_set_h =[]
    for j in data_origin:
        train_set_h.append(j)
    test_set_h.append(data_origin[x])
    for i in test_set_h:
        train_set_h.remove(i)
    print('训练集:',train_set_h,'\n','训练集数量：',len(train_set_h))
    print('测试集:',test_set_h,'\n','测试集数量：',len(test_set_h))

    for data in test_set_h:
        KNN_p = KNN_pro.KNN_pro_Class()
        KNN_o = KNN.KNN_Class()
        d = KNN_o.KNN_original(data, train_set_h)
        #print('\n', '原始型_originalKNN_' * 20)
        #print(d, '\n')
        e = KNN_o.KNN_wd(data, train_set_h)
        #print('\n', '水质距离改进型_wdKNN_' * 20)
        #print(e, '\n')
        a, b, c = KNN_p.KNN_pro_calculate(data, train_set_h)
        #print('\n', '逻辑判断与水质距离改进型_proKNN_' * 20)
        #print('最近项目ID：', a, '\n最近工艺code：', b, '\n最近项目名称：', c)
        for i in code_list:
            ## o算法
            if d == i:  # 预测工艺为i的正类
                if i == data[-2]:  # 样本工艺也为i的正类
                    T_num_o += 1
                    TP_o[i] += 1  # TP增加一个
                else:  # 样本工艺为i的负类
                    FP_o[i] += 1  # FP增加一个
            else:  # 预测工艺为i的负类
                if i == data[-2]:  # 样本工艺为i的正类
                    FN_o[i] += 1  # FN增加一个
                else:  # 样本工艺为i的负类
                    TN_o[i] += 1  # TN增加一个

            ## wd算法
            if e == i:  # 预测工艺为i的正类
                if i == data[-2]:  # 样本工艺也为i的正类
                    T_num_wd += 1
                    TP_wd[i] += 1  # TP增加一个
                else:  # 样本工艺为i的负类
                    FP_wd[i] += 1  # FP增加一个
            else:  # 预测工艺为i的负类
                if i == data[-2]:  # 样本工艺为i的正类
                    FN_wd[i] += 1  # FN增加一个
                else:  # 样本工艺为i的负类
                    TN_wd[i] += 1  # TN增加一个

            ## p算法
            if i in b:  # 预测工艺为i的正类
                if i == data[-2]:  # 样本工艺也为i的正类
                    T_num_p += 1
                    TP_p[i] += 1  # TP增加一个
                else:  # 样本工艺为i的负类
                    FP_p[i] += 1  # FP增加一个
            else:  # 预测工艺为i的负类
                if i == data[-2]:  # 样本工艺为i的正类
                    FN_p[i] += 1  # FN增加一个
                else:  # 样本工艺为i的负类
                    TN_p[i] += 1  # TN增加一个
    count += 1
    print('⭐' * 30, 'LOOCV测试结束第', count, '次','/共', l, '次', '⭐' * 30,'\n\n')

for i in code_list:
    if TP_o[i] + FP_o[i] != 0:
        precision_dict_o[i] = TP_o[i] / (TP_o[i] + FP_o[i])
    if TP_wd[i] + FP_wd[i] != 0:
        precision_dict_wd[i] = TP_wd[i] / (TP_wd[i] + FP_wd[i])
    if TP_p[i] + FP_p[i] != 0:
        precision_dict_p[i] = TP_p[i] / (TP_p[i] + FP_p[i])
    if TP_o[i] + FN_o[i] != 0:
        recall_dict_o[i] = TP_o[i] / (TP_o[i] + FN_o[i])
    if TP_wd[i] + FN_wd[i] != 0:
        recall_dict_wd[i] = TP_wd[i] / (TP_wd[i] + FN_wd[i])
    if TP_p[i] + FN_p[i] != 0:
        recall_dict_p[i] = TP_p[i] / (TP_p[i] + FN_p[i])

accuracy_o = T_num_o / l
accuracy_wd = T_num_wd / l
accuracy_p = T_num_p / l

# 计算总体的F-Measure
fmeasure_dict_o = {}
fmeasure_dict_wd = {}
fmeasure_dict_p = {}
for i in code_list:
    fmeasure_dict_o[i] = fmeasure_dict_wd[i] = fmeasure_dict_p[i] = 0

for i in code_list:
    if precision_dict_o[i] + recall_dict_o[i] != 0:
        fmeasure_dict_o[i] = 2 * precision_dict_o[i] * recall_dict_o[i] / (precision_dict_o[i] + recall_dict_o[i])
    if precision_dict_wd[i] + recall_dict_wd[i] != 0:
        fmeasure_dict_wd[i] = 2 * precision_dict_wd[i] * recall_dict_wd[i] / (precision_dict_wd[i] + recall_dict_wd[i])
    if precision_dict_p[i] + recall_dict_p[i] != 0:
        fmeasure_dict_p[i] = 2 * precision_dict_p[i] * recall_dict_p[i] / (precision_dict_p[i] + recall_dict_p[i])

print('LOOCV测试结束：','\n','accuracy_o：',accuracy_o,'\n','accuracy_wd：',accuracy_wd,'\n','accuracy_p：',accuracy_p,'\n',
      'precision_dict_o：',precision_dict_o,'\n','precision_dict_wd：',precision_dict_wd,'\n','precision_dict_p：',precision_dict_p,'\n',
      'recall_dict_o：',recall_dict_o,'\n','recall_dict_wd：',recall_dict_wd,'\n','recall_dict_p：',recall_dict_p,'\n'
      'fmeasure_dict_o：',fmeasure_dict_o,'\n','fmeasure_dict_wd：',fmeasure_dict_wd,'\n','fmeasure_dict_p：',fmeasure_dict_p,'\n')