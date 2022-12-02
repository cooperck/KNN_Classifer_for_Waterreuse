#选材自开源项目(刘焕勇，中国科学院软件研究所)，数据集来自互联网爬虫数据
import os
import json
from py2neo import Graph,Node
import numpy as np
import pandas as pd
from pandas import DataFrame,Series
import xlrd


class RUWGraph:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        # self.data_path = os.path.join(cur_dir, 'data/reusewater_data_02.json')
        self.g = Graph("http://localhost:7474", username="neo4j", password="cooperck890303")
        self.data_path = xlrd.open_workbook(r'E:\博士论文\\数据结构设计(为分类器准备-改).xlsx')
        self.sheet_no = len(self.data_path.sheets())  # 读取出工作表的数量



    '''读取文件'''
    def read_nodes(self):
        # 构建节点，共 2 类节点
        projects = []  # 项目
        project_infos = []  # 项目信息
        unit_infos = []  # 项目内的单元信息
        rels_proj2unit = []  # 项目－单元包含关系
        rels_unit2unit = []  # 单元-单元的连接关系
        unit_relation_attribute = [] # 单元-单元的连接关系的属性
        fittings_infos =[] # 项目内的零件信息
        rels_unit2fit = [] # 单元-零件的连接关系
        count = 0

        for sheet in range(3,self.sheet_no): # 从每一个项目工作表中读取，前三个为查询表，剔除

            table = self.data_path.sheet_by_index(sheet)
            count += 1
            print("输入第",count,"个项目数据")
            project_info = {} #每个工作表读取形成一个工程项目基础数据的字典
            unit_info = [] #每个工作表读取一个项目所包含的工艺单元的列表
            row_count = table.nrows  # 获取列表的有效行数
            col_count = table.ncols  # 获取列表的有效列数

            ## 各项目名字输入projects
            for headline_row_index in range(row_count):  # 遍历所有行
                for headline_col_index in range(col_count):  # 遍历所有列
                    if table.cell_value(headline_row_index, headline_col_index) == '项目信息层数据格式':  # 定位到查询数据位置
                        headline_marks = [headline_row_index, headline_col_index]  # 得到输入数值所在的行列
                        projectname_row_index = headline_marks[0] + 2
                        projectname_col_index = headline_marks[1] + 1
                        if not table.cell_value(projectname_row_index, projectname_col_index) is '':
                            projects.append(table.cell_value(projectname_row_index,projectname_col_index))


            ## 各工程项目的基础数据字典输入project_infos
            for headline_row_index in range(row_count):  # 遍历所有行
                for headline_col_index in range(col_count):  # 遍历所有列
                    if table.cell_value(headline_row_index, headline_col_index) == '项目信息层数据格式':  # 定位到查询数据位置
                        headline_marks = [headline_row_index, headline_col_index]  # 得到输入数值所在的行列
                        key_row_index = headline_marks[0] + 1
                        value_row_index = headline_marks[0] + 2
                        for key_col_index in range(headline_marks[1], col_count):
                            key = table.cell_value(key_row_index, key_col_index)
                            value = table.cell_value(value_row_index, key_col_index)
                            if value is '':  # 发现有空值的时候停止赋值输入
                                break
                            else:
                                project_info[key] = value

                                for headline_row_index in range(row_count):  # 遍历所有行
                                    for headline_col_index in range(col_count):  # 遍历所有列
                                        if table.cell_value(headline_row_index, headline_col_index) == 'Unit_name':  # 定位到查询数据位置
                                            headline_marks = [headline_row_index, headline_col_index]  # 得到输入数值所在的行列
                                            unit_row_index_start = headline_marks[0] + 1
                                            unit_col_index = headline_marks[1]
                                            value_list = []
                                            for unit_row_index in range(unit_row_index_start, row_count):
                                                value = table.cell_value(unit_row_index, unit_col_index)
                                                if value == 'END' or '':  # 发现有END的时候停止赋值输入
                                                    break
                                                else:
                                                    value_list.append(value)
                                                    project_info['Unit_name'] = value_list
                        if bool(project_info):  # 空字典布尔值为0，不向unit_infos输入
                            project_infos.append(project_info)

            ## 各工程项目的工艺单元信息输入unit_infos
            for headline_row_index in range(row_count):  # 遍历所有行
                for headline_col_index in range(col_count):  # 遍历所有列
                    if table.cell_value(headline_row_index, headline_col_index) == '主要工艺单元的工艺层数据':  # 定位到查询数据位置
                        headline_marks = [headline_row_index, headline_col_index]  # 得到输入数值所在的行列
                        unit_row_index_start = headline_marks[0] + 2  # 设定项目单元起始行
                        unit_col_index_start = headline_marks[1]  # 设定项目单元起始列
                        unit_key_row_index = headline_marks[0] + 1  # 设定项目单元关键字行号
                        i = 0
                        for unit_row_index in range(unit_row_index_start, row_count):  # 每一行代表一个工艺单元逐个输入
                            if table.cell_value(unit_row_index, unit_col_index_start) == 'END':
                                break
                            else:
                                unit_info.append({})  # 开始输入第i个工艺单元数据，每个工艺单元为一个字典
                                for unit_col_index in range(unit_col_index_start, col_count):  # 每一列代表一个工艺单元的属性逐个输入
                                    key = table.cell_value(unit_key_row_index, unit_col_index)
                                    value = table.cell_value(unit_row_index, unit_col_index)
                                    if key == 'Unit_codes':
                                        unit_info[i][key] = []
                                        unit_info[i][key].append(value)  # 输入工艺单元类型代码
                                        # print(unit_info)
                                        unit_info[i][key].append(table.cell_value(unit_row_index,
                                                                                  unit_col_index + 1))  # 工艺单元类型二级代码，防止重复出现两次同一种工艺
                                        # print(unit_info)
                                    elif key == 'Fittings':
                                        unit_info[i][key] = []
                                        for fitting_col_index in range(unit_col_index, col_count):
                                            value = table.cell_value(unit_row_index, fitting_col_index)
                                            if bool(value):  # value布尔值为0，向unit_info输入
                                                unit_info[i][key].append(value)
                                            if not bool(value):
                                                break
                                    elif key == '':
                                        continue
                                    else:
                                        unit_info[i][key] = value
                            i += 1
            if bool(unit_info):  # 空字典布尔值为0，不向unit_infos输入
                unit_infos.append(unit_info)

            ## 各工程项目的工程信息与工艺单元形成联系rels_proj2unit[数组]中每个元素为工程id与单元id组成的[数组]
            for headline_row_index in range(row_count):  # 遍历所有行
                for headline_col_index in range(col_count):  # 遍历所有列
                    if table.cell_value(headline_row_index, headline_col_index) == 'Project_ID':  # 定位到查询数据位置
                        headline_marks = [headline_row_index, headline_col_index]  # 得到输入数值所在的行列
                        ProjID_row_index = headline_marks[0] + 1  # 项目id所在位置
                        ProjID_col_index = headline_marks[1]  # 项目id所在位置
                        for headline_row_index in range(row_count):  # 遍历所有行
                            for headline_col_index in range(col_count):  # 遍历所有列
                                if table.cell_value(headline_row_index, headline_col_index) == 'Unit_ID':  # 定位到查询数据位置
                                    headline_marks = [headline_row_index, headline_col_index]  # 得到输入数值所在的行列
                                    UnitID_row_index_start = headline_marks[0] + 1  # 工艺id所在位置起始
                                    UnitID_col_index = headline_marks[1]  # 工艺id所在位置
                                    for UnitID_row_index in range(UnitID_row_index_start, row_count):
                                        proj_to_unit = []  # 每次定义单个项目到单元的空数组格式
                                        proj_to_unit_1 = table.cell_value(ProjID_row_index,
                                                                          ProjID_col_index)  # proj_to_unit数组中第一个元素(项目ID)
                                        proj_to_unit_2 = table.cell_value(UnitID_row_index,
                                                                          UnitID_col_index)  # proj_to_unit数组中第二个元素(工艺ID)
                                        if proj_to_unit_2 == 'END':
                                            break
                                        else:
                                            proj_to_unit.append(proj_to_unit_1)
                                            proj_to_unit.append(proj_to_unit_2)
                                            if bool(proj_to_unit):  # 空字典布尔值为0，不向rels_proj2unit输入
                                                rels_proj2unit.append(proj_to_unit)

            ## 各工程项目的工艺单元与工艺单元形成联系rels_unit2unit：一个数组，[数组]中每个元素为基于两个单元id的联系[数组]
            for headline_row_index in range(row_count):  # 遍历所有行
                for headline_col_index in range(col_count):  # 遍历所有列
                    if table.cell_value(headline_row_index, headline_col_index) == 'Unitrel_codes_1':  # 定位到查询数据位置
                        headline_marks_rel = [headline_row_index, headline_col_index]  # 得到输入数值所在的行列
                        Unitcode1_row_index_start = headline_marks_rel[0] + 1  # 工艺代码所在位置
                        Unitcode1_col_index = headline_marks_rel[1]            # 工艺代码所在位置

                        for Unitcode1_row_index in range(Unitcode1_row_index_start, row_count):
                            unit_code1 = []
                            unit_code2 = []
                            unit_to_unit = []
                            Unitcode1_1 = table.cell_value(Unitcode1_row_index, Unitcode1_col_index)
                            Unitcode1_2 = table.cell_value(Unitcode1_row_index, Unitcode1_col_index + 1)
                            Unitcode2_1 = table.cell_value(Unitcode1_row_index, Unitcode1_col_index + 2)
                            Unitcode2_2 = table.cell_value(Unitcode1_row_index, Unitcode1_col_index + 3)
                            if Unitcode1_1 == 'END':
                                break
                            else:
                                unit_code1.append(Unitcode1_1)
                                unit_code1.append(Unitcode1_2)
                                unit_code2.append(Unitcode2_1)
                                unit_code2.append(Unitcode2_2)
                                for unit in unit_info:
                                    if unit['Unit_codes'] == unit_code1:
                                        unit_to_unit.append(unit['Unit_ID'])
                                    else:
                                        continue
                                for unit in unit_info:
                                    if unit['Unit_codes'] == unit_code2:
                                        unit_to_unit.append(unit['Unit_ID'])
                                    else:
                                        continue
                                if bool(unit_to_unit):  # 空字典布尔值为0，不向rels_unit2unit输入
                                    rels_unit2unit.append(unit_to_unit)

            ## rels_unit2unit中各工艺单元联系的属性unit_relation_attribute：一个数组，[数组]中每个元素为某个单元单元联系的属性[数组]，他的顺序与rels_unit2unit一致，属性[数组]中的每个数代表了各工艺参数
            for headline_row_index in range(row_count):  # 遍历所有行
                for headline_col_index in range(col_count):  # 遍历所有列
                    if table.cell_value(headline_row_index, headline_col_index) == 'Unitrel_codes_1':  # 定位到查询数据位置
                        headline_marks_rel = [headline_row_index, headline_col_index]  # 得到输入数值所在的行列
                        Unitrelattri_row_index_start = headline_marks_rel[0] + 1  # 工艺链接数据所在位置
                        Unitrelattri_col_index_start = headline_marks_rel[1] + 4  # 工艺链接数据所在位置
                        for Unitrelattri_row_index in range(Unitrelattri_row_index_start, row_count):
                            if table.cell_value(Unitrelattri_row_index, Unitrelattri_col_index_start) == 'END':
                                break
                            Unitrelattri = []
                            for Unitrelattri_col_index in range(Unitrelattri_col_index_start, col_count):
                                unit_rel_attri_data = table.cell_value(Unitrelattri_row_index, Unitrelattri_col_index)
                                if unit_rel_attri_data == '':
                                    break
                                else:
                                    Unitrelattri.append(unit_rel_attri_data)
                                if bool(Unitrelattri):  # 空字典布尔值为0，不向nit_relation_attribute输入
                                    unit_relation_attribute.append(Unitrelattri)

            # 新增一个数组fittings_infos一个数组，[数组]中每个元素为某一个工程的包含的所有零件的信息[数组]，这个数组由代表各零件信息的{字典}组成/
            for headline_row_index in range(row_count):  # 遍历所有行
                for headline_col_index in range(col_count):  # 遍历所有列
                    if table.cell_value(headline_row_index, headline_col_index) == '主要零件的零件数据':  # 定位到查询数据位置
                        headline_marks = [headline_row_index, headline_col_index]  # 得到输入数值所在的行列
                        fitting_row_index_start = headline_marks[0] + 2  # 设定零件元起始行
                        fitting_col_index_start = headline_marks[1]  # 设定零件起始列
                        fitting_key_row_index = headline_marks[0] + 1  # 设定零件关键字行号
                        i = 0
                        fittings_info = []
                        for fitting_row_index in range(fitting_row_index_start, row_count):  # 每一行代表一个工艺单元逐个输入
                            if table.cell_value(fitting_row_index, fitting_col_index_start) == '':
                                break
                            else:
                                fittings_info.append({})
                                for fitting_col_index in range(fitting_col_index_start, col_count):
                                    fitting_key = table.cell_value(fitting_key_row_index, fitting_col_index)
                                    fitting_value = table.cell_value(fitting_row_index, fitting_col_index)
                                    if fitting_key == '':
                                        break
                                    else:
                                        fittings_info[i][fitting_key] = fitting_value
                                i += 1
                        if bool(fittings_info):  # 空字典布尔值为0，不向fittings_infos输入
                            fittings_infos.append(fittings_info)

            ## rels_unit2fit：一个数组，[数组]中每个元素为单元id与零件id组成的[数组]
            for headline_row_index in range(row_count):  # 遍历所有行
                for headline_col_index in range(col_count):  # 遍历所有列
                    if table.cell_value(headline_row_index, headline_col_index) == 'Unit_ID':  # 定位到查询数据位置
                        headline_marks = [headline_row_index, headline_col_index]  # 得到输入数值所在的行列
                        unitID_row_index_start = headline_marks[0] + 1  # 设定零件元起始行
                        unitID_col_index = headline_col_index
                        for col_index in range(col_count):
                            if table.cell_value(headline_row_index, col_index) == 'Fittings':
                                fitting_col_index_start = col_index
                                for unitID_row_index in range(unitID_row_index_start, row_count):  # 每一行代表一个工艺单元逐个输入

                                    if table.cell_value(unitID_row_index, headline_col_index) == 'END':
                                        break
                                    else:
                                        for fitting_col_index in range(fitting_col_index_start, col_count):
                                            rel = []
                                            if table.cell_value(unitID_row_index, fitting_col_index) == '':
                                                break
                                            else:
                                                rel.append(table.cell_value(unitID_row_index, unitID_col_index))
                                                rel.append(table.cell_value(unitID_row_index, fitting_col_index))
                                            if bool(rel):
                                                rels_unit2fit.append(rel)


        print('项目名集合projects',projects)
        print('项目信息集合project_infos',project_infos)
        print('工艺单元集合unit_infos',unit_infos)
        print('项目与单元关系rels_proj2unit', rels_proj2unit)
        print('单元与单元关系rels_unit2unit', rels_unit2unit)
        print('零件集合fittings_infos', fittings_infos)
        print('单元与零件关系rels_unit2fit', rels_unit2fit)

        return set(projects), project_infos, unit_infos, rels_proj2unit, rels_unit2unit, unit_relation_attribute, fittings_infos, rels_unit2fit
        # 返回值为：
        # set(projects)：各工程的id
        # project_infos：一个数组，[数组]中每个元素为某一个工程的基础信息{字典}，如project_infos[0]得到第一个工程的基础数据字典
        # unit_infos：一个数组，[数组]中每个元素为某一个工程的包含的所有单元的信息[数组]，这个数组由代表各工艺单元信息的{字典}组成/
        # 如unit_infos[0][1]代表，第一个工程中第二个单元的基础数据字典，包括name:，id:，规格1:，规格2:,造价：，包含零件：[包含零件1id,包含零件2id,……]
        # 如unit_infos[0][1]['fittings'][1]，第一个工程中第二个单元的第2个零件id
        # rels_proj2unit：一个数组，[数组]中每个元素为工程id与单元id组成的[数组]
        # rels_unit2unit：一个数组，[数组]中每个元素为基于两个单元id的联系[数组]
        # unit_relation_attribute：一个数组，[数组]中每个元素为某个单元单元联系的属性[数组]，他的顺序与rels_unit2unit一致，属性[数组]中的每个数代表了各工艺参数
        ## fittings_infos:一个数组，[数组]中每个元素为某一个工程的包含的所有零件的信息[数组]，这个数组由代表各零件信息的{字典}组成/
        ## rels_unit2fit：一个数组，[数组]中每个元素为单元id与零件id组成的[数组]

    '''建立节点'''
    def create_node(self, label, nodes):
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            print(count, len(nodes))
        return


    '''创建知识图谱中心项目的节点'''
    def create_project_nodes(self, project_infos):
        count = 0
        for project_dict in project_infos:
            node = Node("project", id=project_dict['Project_ID'],name=project_dict['Name'], desc=project_dict['Desc'],
                        category=project_dict['Category1'] ,quantity=project_dict['Quantity'],
                        runtime=project_dict['Run_time'], recovery=project_dict['Recovery'],COD_in=project_dict['COD_in'],
                        CI_in=project_dict['CI_in'], Hardness_in=project_dict['Hardness_in'],
                        ss_in=project_dict['SS_in'], COD_out=project_dict['COD_out'],
                        CI_out=project_dict['CI_out'], Hardness_out=project_dict['Hardness_out'],
                        ss_out=project_dict['SS_out'], COD_emi=project_dict['COD_emi'],
                        CI_emi=project_dict['CI_emi'], Hardness_emi=project_dict['Hardness_emi'],
                        ss_emi=project_dict['SS_emi'],recomand_unit=project_dict['Unit_name'])
            self.g.create(node)
            count += 1
            print("构建project节点：",count)
        return

    '''创建知识图谱工艺单元的节点'''
    def create_unit_nodes(self, unit_infos):
        count = 0
        for unit_p in unit_infos:
            for unit_dict in unit_p:
                node = Node("unit", name=unit_dict['Unit_name'], code=unit_dict['Unit_codes'], id=unit_dict['Unit_ID'],
                            attribute_1=unit_dict['Unit_attribute_1'] ,attribute_2=unit_dict['Unit_attribute_2'],
                            cost=unit_dict['Unit_cost'], fittings=unit_dict['Fittings'])
                self.g.create(node)
                count += 1
                print("构建unit节点：",count)
        return

    '''创建知识图谱零件的节点'''
    def create_fitting_nodes(self, fittings_infos):
        count = 0
        for fitting_p in fittings_infos:
            for fitting_dict in fitting_p:
                node = Node("fitting", name=fitting_dict['Fitting_name'], code=fitting_dict['Fitting_codes'], id=fitting_dict['Fitting_ID'],
                            attribute_1=fitting_dict['Fitting_attribute_1'], attribute_2=fitting_dict['Fitting_attribute_2'],
                            attribute_3=fitting_dict['Fitting_attribute_3'], attribute_4=fitting_dict['Fitting_attribute_4'],
                            attribute_5=fitting_dict['Fitting_attribute_5'], attribute_6=fitting_dict['Fitting_attribute_6'],
                            attribute_7=fitting_dict['Fitting_attribute_7'])
                self.g.create(node)
                count += 1
                # print("构建fitting节点：", count)
        return


    '''创建知识图谱实体节点类型'''
    def create_graphnodes(self):
        projects,  project_infos, unit_infos, rels_proj2unit, rels_unit2unit,\
        unit_relation_attribute, fittings_infos, rels_unit2fit = self.read_nodes()
        self.create_project_nodes(project_infos)
        self.create_unit_nodes(unit_infos)
        self.create_fitting_nodes(fittings_infos)
        print('*'*10,'实体节点构建完成','*'*10)
        return


    '''创建project到unit之间的实体关联边'''  # 定义后给下一个create_graphrels用
    def create_relationship_pro2unit(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.id='%s'and q.id='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return


    '''创建unit之间的实体关联边''' #定义后给下一个create_graphrels用
    def create_relationship_unit(self, start_node, end_node, edges, rel_type, rel_attr): #rel_type关系类型, rel_name关系名字也是关系的属性
        count = 0
        # 去重处理
        set_edges = []
        set_attrs = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))


        for i in range(0,all):
            edge = set_edges[i].split('###')
            attr = rel_attr[i]
            p = edge[0]
            q = edge[1]
            #提取每个水流的各指标
            print(attr[0])
            a_1 = attr[0]
            a_2 = attr[1]
            a_3 = attr[2]
            a_4 = attr[3]
            a_5 = attr[4]
            query = "match(p:%s),(q:%s) where p.id='%s'and q.id='%s' create (p)-[rel:%s{Q:'%s',COD:'%s',Ci:'%s',Hard:'%s',SS:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, a_1, a_2, a_3, a_4, a_5) # 注意id在写入时候要有_,查询不需要下划线
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

    '''创建unit到fitting之间的实体关联边'''  # 定义后给下一个create_graphrels用
    def create_relationship_unit2fit(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.id='%s'and q.id='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return


    '''创建实体关系边'''
    def create_graphrels(self):
        projects, project_infos, unit_infos, rels_proj2unit, rels_unit2unit, \
        unit_relation_attribute, fittings_infos, rels_unit2fit = self.read_nodes()
        # 创建project-unit的关系
        self.create_relationship_pro2unit('project', 'unit', rels_proj2unit, 'contains_unit', '包含的工艺单元')
        #创建unit-unit的关系
        self.create_relationship_unit('unit', 'unit', rels_unit2unit, 'water_flow',unit_relation_attribute)
        # 创建unit-fit的关系
        self.create_relationship_unit2fit('unit', 'fitting', rels_unit2fit, 'contains_fitting', '包含的零件')
        print('*'*10,'实体关系边构建完成','*'*10)
        return


    '''导出数据'''
    def export_data(self):
        projects,  project_infos, unit_infos, rels_proj2unit, rels_unit2unit, \
        unit_relation_attribute, fittings_infos, rels_unit2fit = self.read_nodes()
        # 导出节点名
        f_unit = open('unit211205.txt', 'w+')
        f_project = open('project211205.txt', 'w+')
        l_1=len(unit_infos)
        for i in range(0,l_1):
            l_2 = len(unit_infos[i])
            for j in range(0,l_2):
                f_unit.write(unit_infos[i][j]['Unit_name'])
                if j != l_2 - 1:
                    f_unit.write('\n')
        l_3=len(project_infos)
        for m in range(0,l_3):
            f_project.write(project_infos[m]['Name'])
            if m != l_3 - 1:
                f_project.write('\n')
        f_unit.close()
        f_project.close()

        # 导出各project_infos的dataframe用于分类器
        p_i = {}
        for dict1 in project_infos:
            key_11 = []
            for key_1 in list(dict1.keys()):
                key_11.append(key_1)
            for k1 in key_11:
                p_i[k1] = []   ## project_infos中所有关键字形成一个字典，每个关键字的value暂定为[]
        for dict in project_infos:
            key1=[]
            for key in list(dict.keys()):
                key1.append(key)
            for k in key1:
                p_i[k].append(dict[k])   ## project_infos中所有数值进行赋值
        pi = pd.DataFrame.from_dict(p_i)
        pi.to_excel('project_dataframe211205.xlsx')
        print("*"*10,"project数据已导出至excel","*"*10)
        return






if __name__ == '__main__':
    # 先建立图模型数据库并输出project数据
    handler = RUWGraph()
    handler.export_data()
    handler.create_graphnodes()
    handler.create_graphrels()



## "MATCH (a:unit)-[b:water_flow]->(c:unit) where c.id = '{0}' RETURN a.id".format(i['n.id'])