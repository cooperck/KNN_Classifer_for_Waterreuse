import numpy as np
import xlrd
from QA_ReuseWater_KG import Data_Prepare

'''
做一个改进的KNN算法，来匹配工艺流程，算法流程如下
Step1: 计算测试样本的水质到各训练样本的水质距离（分别计算进水、产水、浓水），水质改进距离是经过类似水质改进型KNN算法进行数据预处理后的L2距离。
Step2: 对距离进行排序（分别对进水、产水、浓水进行排序），输出进水、产水、浓水、总距离最接近的排名前三的样本案例与对应的工艺路线
Step3: 计算所有训练样本之间最大的进水、产水、浓水、总水质距离
Step4: 计算所有训练样本内，同类工艺样本之间，最大的进水、产水、浓水、总水质距离
Step5: 进行距离阈值判断，分为以下几步: 
# Step5.1: 找出在step2中排序的四类距离均排在前三的工艺代码
# Step5.2: 找出符合Step5.1中的工艺代码，且代码对应的进水、产水距离小于训练样本内，同类工艺样本之间进水、产水最大距离
# Step5.3: 找出符合Step5.2中的工艺代码，且代码对应的浓水、总距离至少有一个小于训练样本内，同类工艺样本之间进浓水、总最大距离
# Step5.4: 符合Step5.3中的工艺代码，且代码对应的所有距离必须都达到Step3中的最大进水、产水、浓水、总距离的最大值之内
'''
class KNN_pro_Class:
    ##计算水质距离,输入数据为两个4维list
    def Calculate_WD(self,index_1,index_2):

        '''
        给定COD、CI、Hardness、ss的基础值COD=60 CI=10000 Hardness=450 SS=5（***这个需要调试***）
        '''
        base_value = [50, 1000, 100, 5]
        #计算归一化数值
        index_1_nor = list(map(lambda x: x[0] / x[1], zip(index_1, base_value)))
        index_2_nor = list(map(lambda x: x[0] / x[1], zip(index_2, base_value)))
        # 计算水质距离wd
        v = list(map(lambda x: x[0] - x[1], zip(index_1_nor, index_2_nor)))
        wd = 0
        for i in v:
          wd += i**2
        wd = wd**0.5
        return wd




    def KNN_pro_calculate(self,data_test,data_train):
        DataP = Data_Prepare.DataPrepare()
        # 输入数据，data_dict是工艺代码与工艺流程的字典格式为{1:[工艺流程1],2:[工艺流程2],……}
        # data_origin格式为[[水质数据+工艺流程代号]. [], [] ……]
        # 水质数据顺序： quantity、runtime、recovery、COD_in、CI_in、Hardness_in、ss_in'、
        #               COD_out、CI_out、Hardness_out、ss_out、COD_emi、CI_emi、Hardness_emi、ss_emi、工艺代号,项目id
        data_origin, data_dict = DataP.Data4ClassifierTree()
        print(data_origin)
        print(data_test)
        quantity=data_test[0]
        runtime=data_test[1]
        recovery=data_test[2]

        in_data=data_test[3:7]
        out_data=data_test[7:11]
        emi_data=data_test[11:15]
        if data_test in data_origin:
            data_origin.remove(data_test)

        # quantity = float(input('请输入水量（CMD）： '))
        # runtime = float(input('请输入每日运行时间（h）： '))
        # recovery = float(input('请输入系统回收率（以小数表示）： '))
        # COD_in = float(input('请输入进水COD（mg/L）： '))
        # CI_in = float(input('请输入进水电导率（us/cm）： '))
        # Hardness_in = float(input('请输入进水总硬度（mg/L）： '))
        # ss_in = float(input('请输入进水SS（mg/L）： '))
        # COD_out = float(input('请输入产水COD（mg/L）： '))
        # CI_out = float(input('请输入产水电导率（us/cm）： '))
        # Hardness_out = float(input('请输入产水总硬度（mg/L）： '))
        # ss_out = float(input('请输入产水SS（mg/L）： '))
        # COD_emi = float(input('请输入排水/浓水COD,无外排输入0（mg/L）： '))
        # CI_emi = float(input('请输入排水/浓水电导,无外排输入0（mg/L）： '))
        # Hardness_emi = float(input('请输入排水/浓水总硬度,无外排输入0（us/cm）： '))
        # ss_emi = float(input('请输入排水/浓水SS,无外排输入0（mg/L）： '))



        '''
        逐个计算in out emi三类水质区里距离
        给出进水出水排水距离最近的三个
        给出总水质距离最近的三个
        通过历史数据中的所有水质距离得到历史数据中的最大水质距离，作为水质距离验证的否定最大阈值
        通过历史数据中同类工艺的最大水质距离，作为水质距离验证的确认最大阈值
        '''

        # 存储格式设计为[水质距离，工艺流程，id]
        # 分别存进水、产水、浓水、总水质距离前三名
        low1_in_proj = [9999999, 0, 0]
        low2_in_proj = [9999999, 0, 0]
        low3_in_proj = [9999999, 0, 0]
        low1_out_proj = [9999999, 0, 0]
        low2_out_proj = [9999999, 0, 0]
        low3_out_proj = [9999999, 0, 0]
        low1_emi_proj = [9999999, 0, 0]
        low2_emi_proj = [9999999, 0, 0]
        low3_emi_proj = [9999999, 0, 0]
        low1_wd_proj = [9999999, 0, 0]
        low2_wd_proj = [9999999, 0, 0]
        low3_wd_proj = [9999999, 0, 0]
        # 存储历史数据中的进水、产水、浓水和总水质距离最大值
        wd_in_max = 0
        wd_out_max = 0
        wd_emi_max = 0
        wd_max = 0
        # 存储历史数据中的同类工艺进水、产水、浓水和总水质距离最大值
        wd_process_max_dict = {}

        # 计算与测试数据计算的距离前三名对应的工艺和工程
        for i in data_train:
            in_data_train = i[3:7]
            out_data_train = i[7:11]
            emi_data_train = i[11:15]
            # 分别对进水、产水、浓水的水质距离
            in_wd = self.Calculate_WD(in_data, in_data_train)
            out_wd = self.Calculate_WD(out_data, out_data_train)
            emi_wd = self.Calculate_WD(emi_data, emi_data_train)
            wd = in_wd + out_wd + emi_wd
            print(in_wd, out_wd, emi_wd, wd)
            print('*'*20)
            # 对进、产、浓水距离进行排序，选三个最近的记录data_train中的最后两项，工艺流程和id
            if in_wd < low1_in_proj[0]:
                low1_in_proj[0] = in_wd
                low1_in_proj[1] = i[-2]
                low1_in_proj[2] = i[-1]
            elif in_wd > low1_in_proj[0] and in_wd < low2_in_proj[0]:
                low2_in_proj[0] = in_wd
                low2_in_proj[1] = i[-2]
                low2_in_proj[2] = i[-1]
            elif in_wd > low2_in_proj[0] and in_wd < low3_in_proj[0]:
                low3_in_proj[0] = in_wd
                low3_in_proj[1] = i[-2]
                low3_in_proj[2] = i[-1]

            if out_wd < low1_out_proj[0]:
                low1_out_proj[0] = out_wd
                low1_out_proj[1] = i[-2]
                low1_out_proj[2] = i[-1]
            elif out_wd > low1_out_proj[0] and out_wd < low2_out_proj[0]:
                low2_out_proj[0] = out_wd
                low2_out_proj[1] = i[-2]
                low2_out_proj[2] = i[-1]
            elif out_wd > low2_out_proj[0] and out_wd < low3_out_proj[0]:
                low3_out_proj[0] = out_wd
                low3_out_proj[1] = i[-2]
                low3_out_proj[2] = i[-1]

            if emi_wd < low1_emi_proj[0]:
                low1_emi_proj[0] = emi_wd
                low1_emi_proj[1] = i[-2]
                low1_emi_proj[2] = i[-1]
            elif emi_wd > low1_emi_proj[0] and emi_wd < low2_emi_proj[0]:
                low2_emi_proj[0] = emi_wd
                low2_emi_proj[1] = i[-2]
                low2_emi_proj[2] = i[-1]
            elif emi_wd > low2_emi_proj[0] and emi_wd < low3_emi_proj[0]:
                low3_emi_proj[0] = emi_wd
                low3_emi_proj[1] = i[-2]
                low3_emi_proj[2] = i[-1]

            if wd < low1_wd_proj[0]:
                low1_wd_proj[0] = wd
                low1_wd_proj[1] = i[-2]
                low1_wd_proj[2] = i[-1]
            elif wd > low1_wd_proj[0] and wd < low2_wd_proj[0]:
                low2_wd_proj[0] = wd
                low2_wd_proj[1] = i[-2]
                low2_wd_proj[2] = i[-1]
            elif wd > low2_wd_proj[0] and wd < low3_wd_proj[0]:
                low3_wd_proj[0] = wd
                low3_wd_proj[1] = i[-2]
                low3_wd_proj[2] = i[-1]

        print('进水水质距离前三：')
        print(low1_in_proj)
        print(low2_in_proj)
        print(low3_in_proj)
        print('-'*20)
        print('产水水质距离前三：')
        print(low1_out_proj)
        print(low2_out_proj)
        print(low3_out_proj)
        print('-'*20)
        print('排水水质距离前三：')
        print(low1_emi_proj)
        print(low2_emi_proj)
        print(low3_emi_proj)
        print('-' * 20)
        print('总水质距离前三：')
        print(low1_wd_proj)
        print(low2_wd_proj)
        print(low3_wd_proj)
        print('-' * 20)

        # 计算最大水质距离
        for i in data_train:
            for j in data_train:
                in_data_1 = i[3:7]
                out_data_1 = i[7:11]
                emi_data_1 = i[11:15]
                in_data_2 = j[3:7]
                out_data_2 = j[7:11]
                emi_data_2 = j[11:15]
                wd_in_max_test = self.Calculate_WD(in_data_1, in_data_2)
                wd_out_max_test = self.Calculate_WD(out_data_1, out_data_2)
                wd_emi_max_test = self.Calculate_WD(emi_data_1, emi_data_2)

                wd_max_test = wd_in_max_test + wd_out_max_test + wd_emi_max_test

                if wd_in_max_test > wd_in_max:
                    wd_in_max = wd_in_max_test
                if wd_out_max_test > wd_out_max:
                    wd_out_max = wd_out_max_test
                if wd_emi_max_test > wd_emi_max:
                    wd_emi_max = wd_emi_max_test
                if wd_max_test > wd_max:
                    wd_max = wd_max_test
        print('最大进水距离：',wd_in_max,'最大产水距离：',wd_out_max,'最大浓水距离：',wd_emi_max,'最大总距离：',wd_max)

        # 计算同类工艺的最大距离，存储至一个dict,格式为{工艺代码:[最大进水距离，最大产水距离，最大浓水距离，最大总距离]...}
        for i in data_train:
            wd_in_process_max = 0
            wd_out_process_max = 0
            wd_emi_process_max = 0
            wd_process_max = 0
            in_data_origin_1 = i[3:7]
            out_data_origin_1 = i[7:11]
            emi_data_origin_1 = i[11:15]
            process_code_1 = i[16]
            for j in data_train:
                in_data_origin_2 = j[3:7]
                out_data_origin_2 = j[7:11]
                emi_data_origin_2 = j[11:15]
                process_code_2 = j[16]

                if  process_code_1 == process_code_2:
                    wd_in_max_test = self.Calculate_WD(in_data_origin_1, in_data_origin_2)
                    wd_out_max_test = self.Calculate_WD(out_data_origin_1, out_data_origin_2)
                    wd_emi_max_test = self.Calculate_WD(emi_data_origin_1, emi_data_origin_2)

                    wd_max_test = wd_in_max_test + wd_out_max_test + wd_emi_max_test

                    if wd_in_max_test > wd_in_process_max:
                        wd_in_process_max = wd_in_max_test
                    if wd_out_max_test > wd_out_process_max:
                        wd_out_process_max = wd_out_max_test
                    if wd_emi_max_test > wd_emi_process_max:
                        wd_emi_process_max = wd_emi_max_test
                    if wd_max_test > wd_process_max:
                        wd_process_max = wd_max_test


                    wd_process_max_dict[process_code_1] = [wd_in_process_max,wd_out_process_max,wd_emi_process_max,wd_process_max]
        print('同类工艺的最近距离:', wd_process_max_dict)

        '''
        # 开始进行阈值判断
        # 给定的判断条件为：
        # 1、四类距离均在前三 
        # 2、到这个工艺的进水距离、产水距离小于同类工艺最大距离 
        # 3、浓水距离、总距离中至少一个达到同类工艺最最大距离之内
        # 4、所有距离必须都达到案例中的最大进水、产水、浓水、总距离的最大值之内
        # （***以上标准需要调试***）
        '''

        # 设计一个投票，投满以上四个条件都满足的4票：输出1，不足4票：输出0，0就要进入GAN程序
        vote = 0
        # 1、检验四类距离都在前三的
        process_CODE_1 = [] # 记录均在前三的工艺code
        in_processCODE = [low1_in_proj[1],low2_in_proj[1],low3_in_proj[1]]
        out_processCODE = [low1_out_proj[1],low2_out_proj[1],low3_out_proj[1]]
        emi_processCODE = [low1_emi_proj[1],low2_emi_proj[1],low3_emi_proj[1]]
        all_processCODE = [low1_wd_proj[1],low2_wd_proj[1],low3_wd_proj[1]]
        for i in in_processCODE:
            if i in out_processCODE and i in emi_processCODE and i in all_processCODE:
                process_CODE_1.append(i)
        if len(process_CODE_1) != 0:
            vote += 1
            print('第一项检测完成,vote数：', vote)
            print('第一项检测完成,对应ID：', process_CODE_1)

        # 2、检验到这个工艺的进水、产水距离小于同类工艺最大距离
        process_CODE_2=[] # 记录进水距离小于同类工艺最大进水距离的的工艺
        for i in process_CODE_1:
            #从ID找的对应的工艺号码
            if i == low1_in_proj[1]:
                if low1_in_proj[0] < wd_process_max_dict[i][0]:
                    process_CODE_2.append(i)
            elif i == low2_in_proj[1]:
                if low2_in_proj[0] < wd_process_max_dict[i][0]:
                    process_CODE_2.append(i)
            elif i == low3_in_proj[1]:
                if low3_in_proj[0] < wd_process_max_dict[i][0]:
                    process_CODE_2.append(i)
        process_CODE_22=[] # 记录同时产水距离也小于同类工艺最大产水距离的的工艺
        for i in process_CODE_2:
            # 从ID找的对应的工艺号码
            if i == low1_out_proj[1]:
                if low1_out_proj[0] < wd_process_max_dict[i][1]:
                    process_CODE_22.append(i)
            elif i == low2_out_proj[1]:
                if low2_out_proj[0] < wd_process_max_dict[i][1]:
                    process_CODE_22.append(i)
            elif i == low3_out_proj[1]:
                if low3_out_proj[0] < wd_process_max_dict[i][1]:
                    process_CODE_22.append(i)
        if len(process_CODE_22) != 0:
            vote += 1
            print('第二项检测完成,vote数：',vote)
            print('第二项检测完成,对应ID：', process_CODE_22)

        # 3、检验浓水距离、总距离中至少一个达到同类工艺最大距离之内
        process_CODE_3 = []  # 记录浓水距离小于同类工艺最大浓水距离的的工艺号码
        for i in process_CODE_22:
            if i == low1_emi_proj[1]:
                if low1_emi_proj[0] < wd_process_max_dict[i][2]:
                    process_CODE_3.append(i)
            elif i == low2_emi_proj[1]:
                if low2_emi_proj[0] < wd_process_max_dict[i][2]:
                    process_CODE_3.append(i)
            elif i == low3_emi_proj[1]:
                if low3_emi_proj[0] < wd_process_max_dict[i][2]:
                    process_CODE_3.append(i)
        process_CODE_33 = []  # 记录同时总距离小于同类工艺最大产水距离的的项目ID
        for i in process_CODE_22:
            if i == low1_wd_proj[1]:
                if low1_wd_proj[0] < wd_process_max_dict[i][3]:
                    process_CODE_33.append(i)
            elif i == low2_wd_proj[1]:
                if low2_wd_proj[0] < wd_process_max_dict[i][3]:
                    process_CODE_33.append(i)
            elif i == low3_wd_proj[1]:
                if low3_wd_proj[0] < wd_process_max_dict[i][3]:
                    process_CODE_33.append(i)
        if (len(process_CODE_33) + len(process_CODE_3)) != 0:
            vote += 1
            print('第三项检测完成,vote数：', vote)

        # 4、检验所有距离必须都达到历史案例中的最大进水、产水、浓水、总距离的最大值之内
        # 此时备选工艺代码记录在第二项检测的结果列表process_code_22中
        process_CODE_4 = []  # 记录进水距离小于历史案例中的最大进水距离的的工艺ID
        for i in process_CODE_22:
            if i == low1_in_proj[1]:
                if low1_in_proj[0] < wd_in_max:
                    process_CODE_4.append(i)
            elif i == low2_in_proj[1]:
                if low2_in_proj[0] < wd_in_max:
                    process_CODE_4.append(i)
            elif i == low3_in_proj[1]:
                if low3_in_proj[0] < wd_in_max:
                    process_CODE_4.append(i)
        process_CODE_44 = []  # 记录产水距离同时也小于历史案例中的最大产水距离的的工艺ID
        for i in process_CODE_4:
            if i == low1_out_proj[1]:
                if low1_out_proj[0] < wd_out_max:
                    process_CODE_44.append(i)
            elif i == low2_out_proj[1]:
                if low2_out_proj[0] < wd_out_max:
                    process_CODE_44.append(i)
            elif i == low3_out_proj[1]:
                if low3_out_proj[0] < wd_out_max:
                    process_CODE_44.append(i)
        process_CODE_444 = []  # 记录浓水距离同时也小于历史案例中最大浓水距离的的工艺ID
        for i in process_CODE_44:
            if i == low1_emi_proj[1]:
                if low1_emi_proj[0] < wd_emi_max:
                    process_CODE_444.append(i)
            elif i == low2_emi_proj[1]:
                if low2_emi_proj[0] < wd_emi_max:
                    process_CODE_444.append(i)
            elif i == low3_emi_proj[1]:
                if low3_emi_proj[0] < wd_emi_max:
                    process_CODE_444.append(i)
        process_CODE_4444 = []  # 记录总距离同时也小于历史案例中最大总距离的的工艺ID
        for i in process_CODE_444:
            if i == low1_wd_proj[1]:
                if low1_wd_proj[0] < wd_max:
                    process_CODE_4444.append(i)
            elif i == low2_wd_proj[1]:
                if low2_wd_proj[0] < wd_max:
                    process_CODE_4444.append(i)
            elif i == low3_wd_proj[1]:
                if low3_wd_proj[0] < wd_max:
                    process_CODE_4444.append(i)
        if len(process_CODE_4444) != 0:
            vote += 1
            print('第四项检测完成,vote数：', vote)
            print('第四项检测完成,对应ID：', process_CODE_4444)


        # 输出结果
        if vote == 4:
            # 输出工艺代码出现次数最多的为结果
            process_no = []# 最终工艺流程代码
            process_name = [] # 最终工艺流程
            code_final = max(process_CODE_4444, key=process_CODE_4444.count)
            process_no.append(code_final)
            process_name.append(data_dict[code_final])
            print('最终确定的工艺号码为：', process_no)
            print('最终确定的工艺流程为：', process_name)

        else:
            process_no = []
            process_name = []
            print('未找到合适工艺，vote数：', vote)

        return process_CODE_4444, process_no, process_name

if __name__ == '__main__':
    handler = KNN_pro_Class()
    '''
    输入需求数据
    后期使用验证集数据
    '''
    DataP = Data_Prepare.DataPrepare()
    data_origin, data_dict = DataP.Data4ClassifierTree()
    testlist = [[5000.0, 24, 0.67, 40, 5000, 450, 25, 3, 150, 20, 0, 120, 15000, 1350, 75, None, 1, 'TEST-01'],
                [2000.0, 20, 0.75, 30, 3000, 250, 15, 2, 80, 10, 0, 120, 12000, 1000, 45, None, 1, 'TEST-02'],
                [300.0, 20, 0.75, 50, 8000, 20, 2, 5, 200, 1, 0, 200, 32000, 80, 8, None, 2, 'TEST-03'],
                [10000.0, 22, 0.6, 50, 2000, 40, 5, 2, 50, 2, 0, 125, 5000, 100, 12, None, 2, 'TEST-04'],
                [4000.0, 20, 0.7, 100, 3000, 100, 1, 4, 80, 4, 0, 333, 10000, 333, 12, None, 2, 'TEST-05'],
                [1000.0, 20, 0.85, 45, 2200, 50, 20, 4, 150, 1, 0, 300, 14666, 330, 100, None, 3, 'TEST-06'],
                [100.0, 20, 0.9, 20, 3000, 100, 10, 5, 150, 40, 0, 200, 30000, 1000, 50, None, 3, 'TEST-07'],
                [2000.0, 20, 0.875, 50, 3000, 300, 15, 4, 200, 50, 0, 400, 24000, 2800, 140, None, 3, 'TEST-08'],
                [20000.0, 20, 0.875, 20, 2000, 20, 2, 1, 50, 5, 0, 160, 16000, 160, 5, None, 4, 'TEST-09'],
                [500.0, 22, 0.9, 150, 1700, 100, 5, 5, 50, 3, 0, 1500, 17000, 1000, 30, None, 4, 'TEST-10']]
    train = []
    for j in data_origin:
        train.append(j)
    results = [] # 用于存储测试集的所有结果列表
    for i in testlist:
        result=[] # 用于存储[测试集中的工艺代码,分类后的工艺代码]
        a,b,c=handler.KNN_pro_calculate(i,train)
        result.append(i[16])
        print('result:',result)
        result.append(b) # 就把所有结果输入result,或者把空列表输入
        print('result:',result)
        results.append(result)
    print(results)

    # test=[2000.0, 20, 0.75, 30, 3000, 250, 15, 2, 80, 10, 0, 120, 12000, 1000, 2, None, 1, 'TEST-02']
    # a, b, c = handler.KNN_pro_calculate(test, train)
    # print('ok'*20)
    # print(a,b,c) #分别为距离最近的项目ID，距离最近的工艺号码，距离最近的工艺流程
    # if b != bool:
    #     print("ok")