
import json 

zalo_entities = {
    "PER": "cầu thủ",
    "CLU": "đội bóng", 
    "TME": "mốc thời gian"
}

zalo_entity_pairs = [
    ("CLU", "CLU"),
    ("CLU", "CLU"),
    ("CLU", "PER"),
    ("PER", "TME"),
    ("CLU", "PER"),
    ("PER", "TME"),
    ("PER", "PER"),
    ("PER", "TME")
]

zalo_relations = {
    "COMP": "đấu với",
    "DEFE": "bị đánh bại bởi",
    "SCOP": "ghi bàn cho",
    "SCOT": "là thời điểm ghi bàn của",
    "CARP": "nhận thẻ phạt thuộc",
    "CART": "là thời điểm nhận thẻ phạt của", 
    "SUBP": "thay thế cho",
    "SUBT": "là thời điểm thay thế của"
}

if __name__ == "__main__":
    templates = {"qa_turn1":{},"qa_turn2":{}}
    
    for head_entity, head_entity_name in zalo_entities.items():
        templates['qa_turn1'][head_entity] = "liệt kê tất cả {} trong bài báo.".format(head_entity_name)
        
    for entity_pair, relation in zip(zalo_entity_pairs, zalo_relations.keys()):
        head_entity, tail_entity = entity_pair
        templates['qa_turn2'][str((head_entity, relation, tail_entity))] = \
            "liệt kê {} {} {} XXX.".format(zalo_entities[tail_entity], 
                                           zalo_relations[relation],
                                           zalo_entities[head_entity])    
    with open("zalo_meaningful.json", "w") as f:
        json.dump(templates, f)
                
