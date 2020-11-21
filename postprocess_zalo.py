import json
from collections import defaultdict
from os import listdir
from os.path import isfile, join

# find longest common subsequence to remove team_name inconsistency
def lcs(X, Y): 
    # find the length of the strings 
    m = len(X) 
    n = len(Y) 
  
    # declaring the array for storing the dp values 
    L = [[None]*(n + 1) for i in range(m + 1)] 
  
    """Following steps build L[m + 1][n + 1] in bottom up fashion 
    Note: L[i][j] contains length of LCS of X[0..i-1] 
    and Y[0..j-1]"""
    for i in range(m + 1): 
        for j in range(n + 1): 
            if i == 0 or j == 0 : 
                L[i][j] = 0
            elif X[i-1] == Y[j-1]: 
                L[i][j] = L[i-1][j-1]+1
            else: 
                L[i][j] = max(L[i-1][j], L[i][j-1]) 
  
    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1] 
    return L[m][n] 
# end of function lcs 

def merge_team_time(player_time, player_team, team_only=False, time_only=False):
    """
    team_only: only keep information in which team is available
    time_only: only keep information in which time is available
    """
    pt = defaultdict(list)
    players = set()
    time_players, team_players = set(), set()
    for player, time in player_time:
        pt[player].append(time)
        players.add(player)
        time_players.add(player)

    pc = defaultdict(str)
    for player, club in player_team:
        pc[player] = club 
        players.add(player)
        team_players.add(player)

    # merge information from the above two dictionaries
    result_list = []
    if team_only and time_only:
        iterator = time_players.union(team_players)
    elif team_only:
        iterator = team_players
    elif time_only:
        iterator = time_players
    else:
        iterator = players

    for player in iterator:
        team = pc[player]
        times = pt[player]

        if not times:
            # if time info is not available
            result_list.append({
                "player_name": player.replace('_', ' '),
                "team": team.replace('_', ' '),
                "time": ""
            })
        else:
            for time in times:
                result_list.append({
                    "player_name": player.replace('_', ' '),
                    "team": team.replace('_', ' '),
                    "time": time
                })

    return result_list

def postprocess(prediction_dir, output_file='test_result.jsonl', time_only=False, team_only=False):
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

        team1, team2 = "", "" 

        # 1.check / prioritize COMP relation
        for club1, club2 in relations.get('COMP', []):
            if not club1.isdigit() and not club2.isdigit():
                team1, team2 = club1, club2

        # 2. check SCOP relation
        for _, club in relations.get('SCOP', []):
            if not club.isdigit():
                if lcs(team1, club) == len(team1):
                    team1 = club

                elif lcs(team2, club) == len(team2):
                    team2 = club
  
        # print(f"{test_id} - team1: {team1} - team2: {team2}")

        # 3.check SCOC relation
        for club, _ in relations.get('SCOC', []):
            if not club.isdigit():
                if lcs(team1, club) == len(team1):
                    team1 = club

                elif lcs(team2, club) == len(team2):
                    team2 = club
  
        # print(f"{test_id} - team1: {team1} - team2: {team2}")


        # 4. check CARP relation
        for _, club in relations.get('CARP', []):
            if not club.isdigit():
                if lcs(team1, club) == len(team1):
                    team1 = club

                elif lcs(team2, club) == len(team2):
                    team2 = club
            
        # print(f"{test_id} - team1: {team1} - team2: {team2} ")


        # 5.check CLU entity

        for club in set(entities['CLU']):  
            if not club.isdigit():
                if lcs(team1, club) == len(team1):
                    team1 = club
                
                elif lcs(team2, club) == len(team2):
                    team2 = club

              
        # print(f"{test_id} - team1: {team1.replace('_', ' ')} - team2: {team2.replace('_', ' ')}")

    
        match_summary["players"] = {
            "team1": team1.replace('_', ' '),
            "team2": team2.replace('_', ' ')
        }


        # Get a list of all players name
        players = entities.get('PSC', set())
        
        for player in entities.get('PSA', set()):
            players.add(player)

        for player in entities.get('PSO', set()):
            players.add(player)

        for player, _ in relations.get('SCOT', []):
            players.add(player)

        for player, _ in relations.get('SCOP', []):
            players.add(player)

        for player, _ in relations.get('CARP', []):
            players.add(player)

        for player, _ in relations.get('CART', []):
            players.add(player)

        for player_in, player_out in relations.get('SUBP', []):
            players.add(player_in)
            players.add(player_out)


        # print(f"{test_id} - players: {players}")

        # By default, set score1, score2 = 0, 0 
        team_score_mapping = {team1: 0, team2: 0}

        # Extract all scores possible

        # 1. SCOP relation
        # group player by team => num of players = team score
        for player, team in relations.get('SCOP', []):
            if team_score_mapping.get(team) is not None:
                team_score_mapping[team] += 1

        # 2. SCOC relation
        for team, score in relations.get('SCOC', []):
            if team_score_mapping.get(team) == 0 and score.isdigit():
                team_score_mapping[team] = score

        # 3. SCO 
        # only handle DRAW case
        scores = entities.get('SCO', set())
        try:
            if len(scores) == 1 and (team_score_mapping.get(team1) != 0 and team_score_mapping.get(team2) != 0): # the two teams draw
                team_score_mapping[team1] += 1
                team_score_mapping[team2] += 1
        except:
            pass
            

        match_summary["score_board"] = {
            "score1": str(team_score_mapping[team1]),
            "score2": str(team_score_mapping[team2]) 
        }

        # print(f"{test_id} - score: {team_score_mapping}")

        # WILL POSTPROCESS AGAIN TOMORROW
        # Get score list
        score_list = merge_team_time(relations.get('SCOT', []), relations.get('SCOP', []), 
                            time_only=time_only, team_only=team_only)
        match_summary["score_list"] = score_list
        
        # print(f"{test_id} - score: {score_list}")

        card_list = merge_team_time(relations.get('CART', []), relations.get('CARP', []), 
                                time_only=time_only, team_only=team_only)
        match_summary["card_list"] = card_list

        
        # print(f"{test_id} - score: {card_list}")

        # get substitution list
        sub_list = []
        sub_time = defaultdict(str)

        for player_in, time in relations.get('SUBT', []):
            sub_time[player_in] = time

        for player_in, player_out in relations.get('SUBP', []):
            sub_info = { 
                "player_in": player_in.replace('_', ' '),
                "player_out": player_out.replace('_', ' '),
                "time": sub_time[player_in]
            }
            sub_list.append(sub_info)

        match_summary["substitution_list"] = sub_list

        # print(f"{test_id} - score: {sub_list}")

        test_result.append({
            "test_id": test_id, 
            "match_summary": match_summary
        })

    with open(output_file, 'w') as f:
        for article in test_result:
            json.dump(article, f, ensure_ascii=False)
            f.write('\n')

if __name__ == "__main__":
    postprocess('predictions', time_only=True)

