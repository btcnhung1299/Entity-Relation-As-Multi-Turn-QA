import json
from collections import defaultdict
from os import listdir
from os.path import isfile, join

def postprocess(prediction_dir, output_file='test_result.jsonl'):
    test_result = []
    files = [f for f in listdir(prediction_dir) if isfile(join(prediction_dir, f))]

    for file in files:
        entities = defaultdict(set)
        relations = defaultdict(set)
        test_id = file.split('/')[-1].split('.')[0]

        with open(join(prediction_dir, file), 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            tokens = line.split('\t')

            if len(tokens) == 2:
                entities[tokens[0]].add(tokens[1])
            else:
                relations[tokens[0]].add((tokens[1], tokens[2]))

        match_summary = {}

        # s1 > s2
        s1, s2, st1, st2 = 0, 0, 0, 0
        team1, team2 = "", "" 

        for score in entities.get('SCO', []):
            try:
                s = score.strip().split('-')
                st1, st2 = int(s[0]), int(s[1])
            except:
                try:
                    s = score.strip().split('–')
                    st1, st2 = int(s[0]), int(s[1])
                except:
                    pass 

            if st1 + st2 > s1 + s2:
                s1, s2 = max(st1, st2), min(st1, st2)

        # check if there is a winner
        flag = False
        for club1, club2 in relations.get('DEFE', []):
            team1, team2 = club1, club2 
            flag = True 

        # check if it is a tie
        if not flag:
            for club1, club2 in relations.get('DEFE', []):
                team1, team2 = club1, club2
                flag = True 

        # check if we have another clue
        if not flag:
            for club1, club2 in relations.get('COMP', []):
                team1, team2 = club1, club2

        if not flag:
            if len(entities.get('CLU', [])) == 2:
                team1, team2 = tuple(entities['CLU'])

        match_summary["players"] = {
            "team1": team1,
            "team2": team2
        }

        match_summary["score_board"] = {
            "score1": str(s1),
            "score2": str(s2) 
        }

        # get score list 
        score_list = []
        score_player = {}

        for player, club in relations.get('SCOP', []):
            score_player[player] = club 

        for time, player in relations.get('SCOT', []):
            score_info = {
                "player_name": player,
                "team": score_player.get(player, ""),
                "time": time
            }
            score_list.append(score_info)

        match_summary["score_list"] = score_list

        # get card list 
        card_list = []
        card_player = {}

        for player, club in relations.get('CARP', []):
            card_player[player] = club 

        for time, player in relations.get('CART', []):
            card_info = {
                "player_name": player,
                "team": card_player.get(player, ""),
                "time": time
            }
            card_list.append(card_info)

        match_summary["card_list"] = card_list

        # get substitution list
        sub_list = []
        sub_time = {}

        for player_in, time in relations.get('SUBT', []):
            sub_time[player_in] = time

        for player_in, player_out in relations.get('SUBP', []):
            sub_info = {
                "player_in": player_in,
                "player_out": player_out,
                "time": sub_time.get(player_in, '0')
            }
            sub_list.append(sub_info)

        match_summary["substitution_list"] = sub_list
        test_result.append({
            "test_id": test_id, 
            "match_summary": match_summary
        })

    with open(output_file, 'w') as f:
        for article in test_result:
            json.dump(article, f, ensure_ascii=False)
            f.write('\n')

postprocess('predictions')