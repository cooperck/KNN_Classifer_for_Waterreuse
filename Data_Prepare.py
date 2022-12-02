# -*- coding: utf-8 -*-


import ahocorasick
import os
import json
from py2neo import Graph,Node
import pandas as pd
import xlrd


"""

12月21日后的工作：

可能要新建一个class DataPrepare
构建一个函数从导出的project表格数据中提取project_data（一个[列表]）用于决策树分类器
构建一个函数从图数据库中得到进出水水质与所有工艺连接矩阵（一个[列表]）用于用于GAN生成器鉴别器
构建一个函数从图数据库中得到所有工艺单元的进出水数据，存 unit_data（一个[列表]）用于GAN生成器

"""
class DataPrepare:
    def __init__(self):
        self.g = Graph("http://localhost:7474", username="neo4j", password="cooperck890303")
        self.num_limit = 20
        # 得到所有项目的id,存入[porjid_list]
        sql_projid = "MATCH (a:project) RETURN a.id"
        sql_unitid = "MATCH (a:unit) RETURN a.id"
        self.porjid_listdict = self.g.run(sql_projid).data()
        self.porjid_list = []
        for i in self.porjid_listdict:
            self.porjid_list.append(i['a.id'])
        # 选取project的属性内容
        self.proj_attri = ['quantity', 'runtime', 'recovery',
                      'COD_in', 'CI_in', 'Hardness_in', 'ss_in',
                      'COD_out', 'CI_out', 'Hardness_out', 'ss_out',
                      'COD_emi', 'CI_emi', 'Hardness_emi', 'ss_emi',
                      'cost','recomand_unit']
        # 得到所有工艺单元的id,存入[unitid_list]
        self.unitid_listdict = self.g.run(sql_unitid).data()
        self.unitid_list = []
        for i in self.unitid_listdict:
            self.unitid_list.append(i['a.id'])
        # 选取water_flow的属性内容
        self.water_flow_attri = ['Q', 'COD', 'Ci', 'Hard', 'SS']


    '''
    构建一个函数从导出的project表格数据中提取project_datas（一个[列表]）用于决策树分类器
    project_datas由各project_data列表构成，project_data格式如下[水质数据1，水质数据2，水质数据3，……，[工艺列表],项目id] 其中[工艺列表]为label
    '''
    def Data4ClassifierTree(self):
        # 将每个项目的project数据输入project_data列表中，最后整合到project_datas列表,工艺列表用代号表示
        # 将工艺代号与工艺列表形成一个字典用于反向查询
        project_datas = []
        data_dict = {}
        for id in self.porjid_list:
            project_data = []
            for attri in self.proj_attri:
                sql_runtime = "MATCH (a:project)  where a.id = '%s' RETURN a.%s" % (id,attri)
                atttri_1 = self.g.run(sql_runtime).data()
                project_data.append(atttri_1[0]['a.%s'%(attri)])
            project_data.append(id)
            project_datas.append(project_data)

        print('load data into project_datas：',project_datas)

        # unit_list 用于临时存储各项目的工艺列表
        unit_list = []
        for i in range (len(project_datas)):
            unit_list.append(project_datas[i][-2])

        # unit_list_new 用于存储去重的工艺列表
        unit_list_new = []
        for i in unit_list:
            if i not in unit_list_new:
                unit_list_new.append(i)
        i = 1
        for j in unit_list_new:
            data_dict[i] = j # 工艺代号与工艺列表形成一个字典
            i += 1

        # 工艺代号代替project_datas的最后第二项工艺列表
        for k in range(len(project_datas)):
            value = project_datas[k][-2]
            for key, values in data_dict.items():
                if values == value:
                    project_datas[k][-2] = key
        return project_datas, data_dict


    '''
    构建一个函数从图数据库中得到进、出、浓水水质与所有工艺连接矩阵（每个项目一个[列表]）用于用于GAN生成器鉴别器
    [列表]格式为：[[项目1数据],[项目2数据],……]，[项目1数据]格式为：[水质数据1，水质数据2，……，[工艺code链接矩阵]]
    '''
    def Data4GAN_Links(self):
        unit_links = []
        attri_1= self.proj_attri
        del attri_1[-1] # 提取除了recommendunit以外的所有水质数据
        for proj_id in self.porjid_list:
            unit_link = [] # 每个项目数据输入一个列表
            links = [] # 每个项目的链接矩阵单独存入一个列表
            unit_id_list = [] # 每个项目的工艺id存入一个列表
            # 得到这个项目的所有unit的id
            sql_unit = "MATCH (a:project{id:'%s'})RETURN a.recomand_unit" % (proj_id)
            unit_name_dict = self.g.run(sql_unit).data()
            unit_name_list = unit_name_dict[0]['a.recomand_unit']
            for unit_name in unit_name_list:
                sql_unit_id = "MATCH (a:project{id:'%s'})-[b:contains_unit]->(c:unit{name:'%s'}) RETURN c.id" % (proj_id,unit_name)
                unit_id_dict =self.g.run(sql_unit_id).data()
                unit_id_list.append(unit_id_dict[0]['c.id'])

            # 输入所有水质数据至unit_link
            for attri in attri_1:
                sql_1 = "MATCH (a:project {id:'%s'}) RETURN a.%s" % (proj_id,attri)
                atttri_2 = self.g.run(sql_1).data()
                unit_link.append(atttri_2[0]['a.%s' % (attri)])

            # 输入工艺链接矩阵数据至unit_link
            for unit_id in unit_id_list:
                sql_2 = "MATCH (a:unit{id:'%s'}) RETURN a.code" % (unit_id)
                code_1_dic = self.g.run(sql_2).data()
                code_1 = code_1_dic[0]['a.code']  # code_2为该unit的上游单元代码
                sql_3 = "MATCH (a:unit{id:'%s'})-[b:water_flow]->(c:unit) RETURN c.code" % (unit_id)
                code_2_dic = self.g.run(sql_3).data()
                code_2 = []
                for i in code_2_dic:
                    code_2.append(i['c.code']) # code_2为该unit的下游单元代码，可能为多个
                # print(code_2)
                if bool(code_2):
                    for i in code_2:
                        link = []
                        link.append(code_1)
                        link.append(i)
                        links.append(link)
            unit_link.append(links)
            unit_links.append(unit_link)
            # print(unit_link)
        print('unit_links:', unit_links)
        return unit_links

    '''
    构建一个函数从图数据库中得到所有工艺单元的进出水数据，存入unit_inouts（一个[列表]）用于GAN生成器
    unit_inouts格式为{'工艺单元code1'：[[[进水数据1]，[出水数据1],[排水数据1]],[[进水数据2]，[出水数据2]],……],'工艺单元code2':[[[],[]],……]}
    '''
    '''
    构建一个函数从图数据库中得到所有工艺单元（包括安装自控等）的cost与相关设计参数，存入unit_datas（一个[列表]）用于GAN生成器
    unit_datas格式为[[code1,[进水数据1]，[出水数据1],[排水数据1],[其他工艺参数],[cost],[attri_2],……],[code2,[[],[]],[],……]]
    '''
    def Data4GAN_InOut(self):
        unit_datas = []
        j=0
        for unitid in self.unitid_list:
            unit_inout = []
            unit_in = []
            unit_out = []
            unit_emi = []
            sql_1 = "MATCH (a:unit{id:'%s'})RETURN a.code" % (unitid) # 提取单元的code
            code_all = self.g.run(sql_1).data()
            code_1 = code_all[0]['a.code'][0] # 提取单元的主code
            #print(code_1)

            # 从数据库得到各单元的进水数据，进水有多组数据的以列表形式存入unit_in，水质参数顺序为'Q', 'COD', 'Ci', 'Hard', 'SS'
            for attri in self.water_flow_attri:
                # 读取进入这个单元的所有水源数据
                attri_1 =[] # 临时存储进水数据
                sql_2 = "MATCH (a:unit)-[b:water_flow]->(c:unit{id:'%s'}) RETURN b.%s" % (unitid, attri)
                flow_in_attri_1 = self.g.run(sql_2).data()
                # print(flow_in_attri_1)
                # 提取flow_in_attri_1中的值，flow_in_attri_1格式为：[{'b.Q': '276.0'},{'b.Q': '1.0'},{}……]
                if len(flow_in_attri_1) != 0:
                    for i in range(0,len(flow_in_attri_1)):
                        attri_1.append(list(flow_in_attri_1[i].values())[0])
                    attri_1 = [float(x) for x in attri_1]
                    #print(attri_1)
                unit_in.append(attri_1) #水质参数顺序为'Q', 'COD', 'C ', 'Hard', 'SS',可能会有多个数据，多个数据为列表形式

                # 读取流出这个单元的所有水源数据，浓度高的作为浓水，浓度低的作为产水
                attri_2 = []  # 临时存储产水数据
                attri_3 = []  # 临时存储浓水数据
                sql_3 = "MATCH (a:unit{id:'%s'})-[b:water_flow]->(c:unit) RETURN b.%s" % (unitid, attri)
                flow_outemi_attri_2 = self.g.run(sql_3).data()
                # print(flow_outemi_attri_2)
                if len(flow_outemi_attri_2) > 1: # 有两个值时最小值为产水、最大值为浓水
                    out_value = float(list(flow_outemi_attri_2[0].values())[0])
                    emi_value = float(list(flow_outemi_attri_2[1].values())[0])
                    if attri == 'Q':
                        if out_value < emi_value:
                            out_value , emi_value =  emi_value , out_value
                    else:
                        if out_value > emi_value:
                            out_value , emi_value =  emi_value , out_value
                    attri_2.append(out_value)
                    attri_3.append(emi_value)
                    unit_out.append(attri_2)
                    unit_emi.append(attri_3)
                elif len(flow_outemi_attri_2) == 1: # 有只有一个值或没有时，值就是产水，没有浓水
                    out_value = float(list(flow_outemi_attri_2[0].values())[0])
                    attri_2.append(out_value)
                    unit_out.append(attri_2)
                    unit_emi.append(attri_3)
                else:
                    unit_out.append(attri_2)
                    unit_emi.append(attri_3)
            # 记录每个工艺单元的cost数据
            sql_4 = "MATCH (a:unit{id:'%s'})RETURN a.cost" % (unitid)  # 提取单元的code
            cost_1 = self.g.run(sql_4).data()
            cost_2 = list(cost_1[0].values())
            if bool(cost_2[0]):
                cost = cost_2
            else:
                cost=[]

            # 记录每个工艺单元的配置等级数据
            sql_4 = "MATCH (a:unit{id:'%s'})RETURN a.attribute_2" % (unitid)  # 提取单元的code
            attribute_2_1 = self.g.run(sql_4).data()
            attribute_2_2 = list(attribute_2_1[0].values())
            if bool(attribute_2_2[0]):
                attribute_2 = attribute_2_2
            else:
                attribute_2 = []


            # print(attribute_2)


            # print('unit_in',unit_in)
            # print('unit_out', unit_out)
            # print('unit_emi', unit_emi)
            # print('cost',cost)

            # 将一个unit的数据以unit_inout列表形式输入unit_datas列表
            unit_inout.append(code_1)
            unit_inout.append(unit_in)
            unit_inout.append(unit_out)
            unit_inout.append(unit_emi)
            unit_inout.append(cost)
            unit_inout.append(attribute_2)
            unit_datas.append(unit_inout)
            j+=1
            print('load',j,'datas')



        return unit_datas


    '''
    构建一个函数从图数据库中得到所有工程的[总投资，安装价格，自控价格，电缆桥架价格，管阀件价格，运输费，设计与调试费]，存入unit_inouts（一个[列表]）用于GAN生成器
    '''

    def Data4GAN_Cost(self):
        costs = []
        for proj_id in self.porjid_list:
            cost = []  # 每个项目数据输入一个列表
            # 得到这个项目的所有unit的id
            sql_cost_proj = "MATCH (a:project{id:'%s'})RETURN a.cost" % (proj_id)
            proj_cost_dict = self.g.run(sql_cost_proj).data()
            cost_proj = proj_cost_dict[0]['a.cost']
            cost.append(cost_proj)
            public_list=['安装','自控','电缆桥架','管阀件','运输费','设计与调试费']
            for unit_name in public_list:
                sql_unit_id = "MATCH (a:project{id:'%s'})-[b:contains_unit]->(c:unit{name:'%s'}) RETURN c.cost" % (proj_id,unit_name)
                public_cost_dict =self.g.run(sql_unit_id).data()
                cost.append(public_cost_dict[0]['c.cost'])
            costs.append(cost)
        return costs



if __name__ == '__main__':
    # 为决策树与GAN准备结构画数据
    handler = DataPrepare()
    project_datas, data_dict = handler.Data4ClassifierTree()
    unit_links = handler.Data4GAN_Links()
    unit_datas = handler.Data4GAN_InOut()
    costs=handler.Data4GAN_Cost()
    print('project_datas：', project_datas) ## project_datas格式为[[水质数据+工艺流程代号]. [], [] ……]
    print('data_dict：', data_dict)         ## data_dict格式为{1:[工艺流程1],2:[工艺流程2],……}
    print('unit_links：', unit_links)
    print('unit_datas：', unit_datas)
    print('public-cost：', costs)

    # print('单元链接project_datas：', project_datas)
    # handler.Data4GAN_InOut()

## MATCH (a:unit)-[b:water_flow]->(c:unit) where c.id = '{0}' RETURN a.id".format(i['n.id'])
## "MATCH (a:project {id:'%s'})-[b:contains_unit]->(c:unit) where a.id = '进水' RETURN c.id" % (proj_id)