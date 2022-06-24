import json
import random

from utils import *
from valid_sub_attr_grader import *


class PossLoader:

    def __init__(self, drop_poss_path, item_poss_path):

        self.item_pos_list = []
        self.main_attr_list = []
        self.main_attr_poss_map = {}

        # 初始化主词条概率矩阵
        with open(drop_poss_path, "r", encoding="utf8") as fin:

            for idx, line_str in enumerate(fin.readlines()):
                item_pos_strs = line_str.strip().split(",")
                
                if idx == 0:
                    for i in range(1, len(item_pos_strs)):
                        self.item_pos_list.append(item_pos_strs[i])
                        self.main_attr_poss_map[item_pos_strs[i]] = {}
                else:
                    main_attr_name = item_pos_strs[0]
                    self.main_attr_list.append(main_attr_name)
                    for i in range(1, len(item_pos_strs)):
                        self.main_attr_poss_map[self.item_pos_list[i-1]][main_attr_name] = float(item_pos_strs[i])
        
        self.sub_attr_poss_map = {}
        self.sub_attr_list = []
        # 初始化副次条概率矩阵
        with open(item_poss_path, "r", encoding="utf8") as fin:

            for idx, line_str in enumerate(fin.readlines()):
                item_pos_strs = line_str.strip().split(",")
                
                if idx == 0:
                    for i in range(1, len(item_pos_strs)):
                        self.sub_attr_list.append(item_pos_strs[i])
                else:
                    main_attr_name = item_pos_strs[0]
                    self.sub_attr_poss_map[main_attr_name] = {}
                    for i in range(1, len(item_pos_strs)):
                        self.sub_attr_poss_map[main_attr_name][self.sub_attr_list[i-1]] = float(item_pos_strs[i])


    def check_print(self):
        print(json.dumps(self.main_attr_poss_map, indent=4, ensure_ascii=False))
        print(json.dumps(self.sub_attr_poss_map, indent=4, ensure_ascii=False))


    def random_draw(self, item_pos=None, main_attr=None):
        if item_pos is None:
            item_pos = random.choice(self.item_pos_list)
        if main_attr is None:
            main_attr = random_choice_one_among_poss_map(self.main_attr_poss_map[item_pos])
        sub_attr_map = {}
        sub_attr_set = random_choice_multi_among_poss_map(self.sub_attr_poss_map[main_attr], 4)

        base_sub_attr_num = random.randrange(3, 5)
        sub_attr_total_num = base_sub_attr_num + 1

        sub_attr_num = [1, 1, 1, 1]
        for i in range(sub_attr_total_num):
            sub_attr_num[random.randrange(0, 4)] += 1
        sub_attr_map = {}
        for idx, sub_attr_name in enumerate(sub_attr_set):
            sub_attr_map[sub_attr_name] = sub_attr_num[idx]
        return ItemDetail(item_pos, main_attr, sub_attr_map, base_sub_attr_num)
        

        