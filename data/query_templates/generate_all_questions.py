
import json 

zalo_entity_tags = [
    "CLU", 
    "SCO",
    "PSC",
    "PCA", 
    "PSO",
    "PSI",
    "TSC",
    "TCA", 
    "TSI"
    # CLU: clb
    # SCO: số lượng bàn
    # PSC: cầu thủ ghi bàn
    # PCA: cầu thủ nhận thẻ
    # PSO: cầu thủ ra sân
    # PSI: cầu thủ vào sân
    # TSC: thời gian ghi bàn
    # TCA: thời gian nhận thẻ
    # TSI: thời gian vào sân/ra sân
]

zalo_entity_names = [
    "câu lạc bộ",
    "số bàn thắng",
    "cầu thủ ghi bàn", 
    "cầu thủ nhận thẻ",
    "cầu thủ ra sân",
    "cầu thủ thay thế",
    "thời gian ghi bàn",
    "thời gian nhận thẻ",
    "thời gian vào sân"
]

zalo_relation_tags = [
    "COMP", # CLU - CLU
    "SCOC", # CLU - SCO
    "SCOP", # PSC - CLU 
    "SCOT", # PSC - TSC
    "CARP", # PCA - CLU
    "CART", # PCA - TCA
    "SUBP", # PSI - PSO
    "SUBT"  # PSI - TSI
]

zalo_relations_names = [
    "đấu với",
    "đạt được",
    "lập công cho",
    "lập công tại",
    "thuộc",
    "nhận thẻ tại",    
    "thay thế cho",
    "vào sân tại"
]


if __name__ == "__main__":
    templates = {"qa_turn1":{},"qa_turn2":{}}
    
    for head_entity, head_entity_name in zip(zalo_entity_tags, zalo_entity_names):
        templates['qa_turn1'][head_entity] = "liệt kê tất cả {}.".format(head_entity_name)
        
        for relation, relation_name in zip(zalo_relation_tags, zalo_relations_names):
            for tail_entity, tail_entity_name in zip(zalo_entity_tags, zalo_entity_names):
                templates['qa_turn2'][str((head_entity, relation, tail_entity))] = \
                    "{} XXX {} {} nào?".format(head_entity_name, relation_name, tail_entity_name)
                
    with open("zalo_all.json", "w") as f:
        json.dump(templates, f, ensure_ascii=False)
                
