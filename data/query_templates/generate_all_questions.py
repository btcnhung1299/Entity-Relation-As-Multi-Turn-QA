
import json 

zalo_entity_tags = [
    "PER",   # player
    "CLU",   # club
    "TME"   # time
]

zalo_entity_names = [
    "cầu thủ",
    "đội bóng",
    "mốc thời gian"
]

zalo_relation_tags = [
    "COMP",  # (CLU, CLU) compete with
    "DEFE",  # (CLU, CLU) defeat / win over
    "SCOP",  # (CLU, PER) score player
    "SCOT",  # (PER, TME) score time
    "CARP",  # (CLU, PER) card player,
    "CART",  # (PER, TIME) card time
    "SUBP",  # (PER, PER) substitute players,
    "SUBT",  # (PER, TIME) substitute time
]

zalo_relations_names = [
    "đấu với",
    "bị đánh bại bởi",
    "ghi bàn cho",
    "là thời điểm ghi bàn của",
    "nhận thẻ phạt thuộc",
    "là thời điểm nhận thẻ phạt của",    
    "thay thế cho",
    "là thời điểm thay thế của"
]


if __name__ == "__main__":
    templates = {"qa_turn1":{},"qa_turn2":{}}
    
    for head_entity, head_entity_name in zip(zalo_entity_tags, zalo_entity_names):
        templates['qa_turn1'][head_entity] = "liệt kê tất cả {} trong bài báo.".format(head_entity_name)
        
        for relation, relation_name in zip(zalo_relation_tags, zalo_relations_names):
            for tail_entity, tail_entity_name in zip(zalo_entity_tags, zalo_entity_names):
                templates['qa_turn2'][str((head_entity, relation, tail_entity))] = \
                    "liệt kê {} {} {} XXX.".format(tail_entity_name, relation_name, head_entity_name)
                
    with open("zalo_all.json", "w") as f:
        json.dump(templates, f)
                
