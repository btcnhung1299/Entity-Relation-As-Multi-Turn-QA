import json
from collections import defaultdict
from os import listdir
from os.path import isfile, join

def mapping(name, reference):
    # check if reference if the full name of input name
    if name == reference:
        return name

    if reference.find(name) != -1:
        return reference
        
    return name 

def merge_team_time(player_time, player_team, name_mapping, team_only=False, time_only=False):
    """
    team_only: only keep information in which team is available
    time_only: only keep information in which time is available
    """
    pt = defaultdict(list)
    players = set()
    for time, player in player_time:
        pt[name_mapping[player]].append(time)
        players.add(name_mapping[player])

    pc = defaultdict(str)
    for player, club in player_team:
        pc[name_mapping[player]] = club 
        players.add(name_mapping[player])

    # merge information from the above two dictionaries
    result_list = []
    iterator = players if not team_only else [name_mapping[player] for player, _ in player_team]
    for player in iterator:
        team = pc[player]
        times = pt[player]

        if not times:
            # if time info is not available
            result_list.append({
                "player_name": player,
                "team": team,
                "time": ""
            })
        else:
            for time in times:
                result_list.append({
                    "player_name": player,
                    "team": team,
                    "time": time
                })

    return result_list

def postprocess(prediction_dir, output_file='test_result.jsonl', full_name=False):
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
            for club1, club2 in relations.get('DRAW', []):
                team1, team2 = club1, club2
                flag = True 

        # check if we have another clue
        if not flag:
            for club1, club2 in relations.get('COMP', []):
                team1, team2 = club1, club2
                flag = True 

        if not flag:
            try: 
                teams = list(entities['CLU'])
                team1 = teams[0]
                team2 = teams[1]
            except:
                pass 

        match_summary["players"] = {
            "team1": team1,
            "team2": team2
        }

        match_summary["score_board"] = {
            "score1": str(s1),
            "score2": str(s2) 
        }
        # mapping from name to ful name
        name_mapping = {player: player for player in players}

        if full_name:
            # get a list of all players name
            players = entities.get('PER', set())
            for _, player in relations.get('SCOT', []):
                players.add(player)
            for _, player in relations.get('CART', []):
                players.add(player)
            for player, _ in relations.get('SCOP', []):
                players.add(player)
            for player, _ in relations.get('CARP', []):
                players.add(player)
            for player_in, player_out in relations.get('SUBP', []):
                players.add(player_in)
                players.add(player_out)
            
            players = list(players)

            for name in players:
                for reference in players:
                    full_name = mapping(name, reference)
                    if len(full_name) > len(name_mapping[name]):
                        name_mapping[name] = full_name

        score_list = merge_team_time(relations.get('SCOT', []), relations.get('SCOP', []), name_mapping, team_only=True)
        match_summary["score_list"] = score_list

        card_list = merge_team_time(relations.get('CART', []), relations.get('CARP', []), name_mapping)
        match_summary["card_list"] = card_list

        # get substitution list
        sub_list = []
        sub_time = defaultdict(str)

        for time, player_in in relations.get('SUBT', []):
            try:
                sub_time[name_mapping[player_in]] = time
            except:
                print(time, player_in)

        for player_in, player_out in relations.get('SUBP', []):
            sub_info = { 
                "player_in": name_mapping[player_in],
                "player_out": name_mapping[player_out],
                "time": sub_time[name_mapping[player_in]]
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

if __name__ == "__main__":
    postprocess('predictions', 'test_result_18_2011.jsonl')