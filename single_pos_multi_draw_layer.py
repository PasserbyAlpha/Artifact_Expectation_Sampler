import json
import os
from random import sample
from poss_loader import PossLoader
from single_pos_single_draw_layer import PaLayer
from utils import random_choice_one_among_poss_map


class PsLayer:
    # 用于计算一个指定组件T次抽取的有效词次条数量的概率分布

    def __init__(self, poss_loader:PossLoader, pa_layer:PaLayer, MAX_T=10000, allow_cache=True):
        self.poss_loader = poss_loader
        self.pa_layer = pa_layer
        self.MAX_T = MAX_T
        self.item_sub_t_poss = {}

        cache_path = self.cache_path()
        if allow_cache and os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf8") as fin:
                self.item_sub_t_poss = json.loads(fin.read())
            print("已加载Ps缓存")
        else:
            self.init_poss_distribute()

        # print(json.dumps(self.item_sub_t_poss["沙"][1], indent=4, ensure_ascii=False))    
        # print(json.dumps(self.item_sub_t_poss["沙"][10], indent=4, ensure_ascii=False))
        # print(json.dumps(self.item_sub_t_poss["沙"][100], indent=4, ensure_ascii=False))
        # print(json.dumps(self.item_sub_t_poss["沙"][1000], indent=4, ensure_ascii=False))
        # print(json.dumps(self.item_sub_t_poss["沙"][10000], indent=4, ensure_ascii=False))

    def cache_path(self):
        return "ps_layer_cache_{}_{}.cache".format(self.MAX_T, self.pa_layer.grader.rule_hash)


    def init_poss_distribute(self, sample_time=1000):
        self.item_sub_t_poss = {}
        for item_pos in self.poss_loader.item_pos_list:
            self.item_sub_t_poss[item_pos] = []
            for t in range(self.MAX_T):
                self.item_sub_t_poss[item_pos].append({})
                for score_idx in range(0, 19):
                    self.item_sub_t_poss[item_pos][t][str(score_idx*0.5)] = 0
            
            self.item_sub_t_poss[item_pos][0]["0.0"] = 1
            for st in range(sample_time):
                if (st+1) % (sample_time / 10) == 0:
                    print("{}%".format(st/sample_time*100))
                max_m = 0.0
                for t in range(1, self.MAX_T):
                    new_score = float(self.pa_layer.draw(item_pos))
                    max_m = max(max_m, new_score // 0.5 * 0.5)
                    self.item_sub_t_poss[item_pos][t][str(max_m)] += 1
            for t in range(1, self.MAX_T):
                for score_idx in range(19):
                    self.item_sub_t_poss[item_pos][t][str(score_idx*0.5)] /= sample_time

        
        with open(self.cache_path(), "w", encoding="utf8") as fout:
            fout.write(json.dumps(self.item_sub_t_poss, indent=4, ensure_ascii=False))

        print("单个部位多抽最优副次条数量概率分布预计算完成")


    def draw(self, item_pos, t):
        # 对部件item_pos抽取t次得到m
        return random_choice_one_among_poss_map(self.item_sub_t_poss[item_pos][t])
