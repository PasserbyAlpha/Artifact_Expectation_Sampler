import json
import os
import numpy
from poss_loader import PossLoader
from single_pos_multi_draw_layer import PsLayer



MAX_TOTAL_SUB = 46
MAX_TOTAL_SUB_IDX = 91

class PLayer41:
    # 用于计算一个指定组件T次抽取的有效词次条数量的概率分布

    def __init__(self, poss_loader:PossLoader, ps_layer:PsLayer, single_piece_Q=10, allow_cache=False, target_t_list=[35, 70, 140, 140*2, 140*3, 140*6, 140*12]):
        self.poss_loader = poss_loader
        self.ps_layer = ps_layer
        self.single_piece_Q = single_piece_Q
        
        self.combine_m_t_poss = {}

        self.target_t_list = target_t_list

        self.init_poss_distribute()


    def init_poss_distribute(self, sample_time=10000):
        self.combine_m_t_poss = {}

        sample_num = {}

        for t in self.target_t_list:
            self.combine_m_t_poss[t] = {}
            sample_num[t] = 0
            for i in range(MAX_TOTAL_SUB_IDX):
                self.combine_m_t_poss[t][str(i*0.5)] = 0
        
        def dfs(sub_attr_num_list, sub_attr_single_piece_list, current_attr_num, current_item_pos_idx, is_single_piece_used=False):
            
            if current_item_pos_idx >= len(self.poss_loader.item_pos_list):
                return current_attr_num
            
            # 使用套间内圣遗物
            current_max_compose = dfs(
                sub_attr_num_list,
                sub_attr_single_piece_list,
                current_attr_num+sub_attr_num_list[current_item_pos_idx],
                current_item_pos_idx+1,
                is_single_piece_used
            )

            if not is_single_piece_used:
                current_max_compose = max(current_max_compose, dfs(
                    sub_attr_num_list,
                    sub_attr_single_piece_list,
                    current_attr_num+sub_attr_single_piece_list[current_item_pos_idx],
                    current_item_pos_idx+1,
                    True
                ))
            
            return current_max_compose


        BASE_POSS_LIST = [0.2] * 5
        for t in self.target_t_list:
            print("正在模拟{}件套装圣遗物情况".format(t))
            current_temp_sample_time = sample_time


            draw_result = numpy.random.multinomial(t, BASE_POSS_LIST, (current_temp_sample_time, ))
            for st in range(current_temp_sample_time):
                # 多项式分布抽样
                single_draw_result = draw_result[st, :]
                current_sub_list = []
                current_replace_sub_list = []
                for i in range(len(self.poss_loader.item_pos_list)):
                    current_sub_list.append(float(self.ps_layer.draw(self.poss_loader.item_pos_list[i], single_draw_result[i])))
                    current_replace_sub_list.append(float(self.ps_layer.draw(self.poss_loader.item_pos_list[i], single_draw_result[i]*self.single_piece_Q)))
                
                result = dfs(current_sub_list, current_replace_sub_list, 0.0, 0, False)
                self.combine_m_t_poss[t][str(result)] += 1
                sample_num[t] += 1
            
        # 归一化
        for t in self.target_t_list:
            if sample_num[t] == 0:
                continue
            for m in range(MAX_TOTAL_SUB_IDX):
                self.combine_m_t_poss[t][str(m*0.5)] /= sample_num[t]

    
    def get_expectation(self):
        result_dict = {}
        for t in self.target_t_list:
            expected_sub_attr = 0
            for m in range(MAX_TOTAL_SUB_IDX):
                expected_sub_attr += m*0.5 * self.combine_m_t_poss[t][str(0.5*m)]
            result_dict[t] = expected_sub_attr
        return result_dict

    def check_print(self):
        print(json.dumps(self.get_expectation(), indent=4, ensure_ascii=False))
