# Zalo AI Challenge 2020 - News Summarization

This is the solution write-up of team **NKT** for the News Summarization Track of Zalo AI Challenge 2020.

Our team members:
- [Nhung Bui](https://www.linkedin.com/in/nhung-bui-795006128/)
- [Khanh Nguyen](https://www.linkedin.com/in/ndkhanh/)
- [Tam Nguyen](https://www.linkedin.com/in/nnbtam99/)
- [Tu Huynh](https://github.com/tuhyn)
- [Nhat Le](https://github.com/minhnhatvt)

# Approach

## Pre-processing

Training dataset was created from a subset of features in the provided dataset, including:

- `match_summary`
- `html_annotation`
- `train_id` (for file identity only)

We follow the format of ACE2004, a dataset for the task of entity/relation extraction, and introduce new type of entities and relations regarding the current problem.


| Entity | Meaning                    | Entity's Vietnamese name    |
| -------- | -------------------------- |:------------------ |
| CLU      | Team                       | câu lạc bộ         |
| SCO      | Team goals                 | số bàn thắng       |
| PSC      | Player who scored          | cầu thủ ghi bàn    |
| PCA      | Player who received a card | cầu thủ nhận thẻ   |
| PSI      | Substitute                 | cầu thủ thay thế   |
| PSO      | Player who was replaced    | cầu thủ ra sân     |
| TSC      | Time when a player scored | thời gian ghi bàn  |
| TCA      | Time when a card is shown | thời gian nhận thẻ |
| TSI      | Time when substitution happened | thời gian vào sân |


| Relation  | Meaning                            | Relation's Vietnamese name     |
| -------------- | ---------------------------------- |:------------------------------ |
| COMP(CLU, CLU) | compete against | đấu với                        |
| SCOC(CLU, SCO) | score | đạt được bởi |
| SCOP(PSC, CLU) | score for | có pha lập công của            |
| SCOT(PSC, TSC) | score at | là thời điểm lập công của      |
| CARP(PCA, CLU) | carded as a player of | có thẻ phạt từ                 |
| CART(PCA, TCA) | carded at | là thời điểm nhận thẻ phạt của |
| SUBP(PSI, PSO) | substitute for | bị thế chỗ bởi                 |
| SUBT(PSI, TME) | substitute at | là thời điểm bắt đầu của       |

We use heuristic matching method to find the position of entities within and without relations:

- `SCO`: We prioritize text inside a score pattern `score - score` (e.g., 4 - 2, 2 - 3) for matching.
- We use perfect matching to identify position of other entities. To handle short forms (e.g. Pogba short for Paul Pogba), we keep looking for subwords matching in the referenced events if no perfect match found.

Text in `html_annotation` was segmentized using [VnCoreNLP toolkit](https://github.com/vncorenlp/VnCoreNLP) and concatenated as a sample. Next, we encoded information in `match_summary` as entities and relations using matching method explained above. Note that entity position found within referenced events were converted to absolute position within the full content.

We only use the data created following this procedure to train our model and do not use any external data.

## Model

Our approach for this challenge was primarily based on the paper titled "[Entity-Relation Extraction as Multi-Turn Question Answering](https://arxiv.org/abs/1905.05529)". To extract specific information from sport report, we cast the task to jointly entity-relation extraction with entities and relations. This task was indirectly solved as question answering problem:

- To extract entities, simply state it in the single question.
- To extract multiple entities in a relation, we need to answer questions in multiple turns. Due to time constraints, we only consider relations which can be extracted in two turns of question-answer.

We used [PhoBERT](https://arxiv.org/abs/2003.00744) as feature extractor, followed by a classification head. Each token is classified into one of 5 tags B, I, O, E, S (see [also](https://en.wikipedia.org/wiki/Inside%E2%80%93outside%E2%80%93beginning_(tagging))) similar to typical sequence tagging problem.

Firstly, segmentized content was fed to the model to classify tag of each token. An entity was constituted by considering all tokens between B and E tags. These entities served as head entities in relations, which were replaced in proper template to form questions. Answers to these questions result in tail entities of relations. 

More specifically, we extract all the entities belong to 9 NER types above in the first turn. The question template for this turn is 

> **Liệt kê tất cả** `[Entity's Vietnamese name]`.

*Example*: The question for extracting all `CLU` entities is "**Liệt kê tất cả [câu lạc bộ]**".

The extracted entities will then be used as the head entities in the question template for the second turn.

> `[Tail entity's Vietnamese name]` **nào** `[relation's Vietnamese name]` `[head entity's Vietnamese name]` `[extracted head entity's value]`

*Example*: To extract the tail entity club (`CLU`) that competes with the head entity U22 Việt Nam (`CLU`), the question for the corresponding relation `COMP(CLU, CLU)` is "**[Câu lạc bộ] nào [đấu với] [câu lạc bộ] [U23 Việt Nam]**".

To reflect the jointly extraction method, the loss function took into account loss of both entites and relation extraction phase:

<a href="https://www.codecogs.com/eqnedit.php?latex=\dpi{120}&space;L&space;=&space;(1-\lambda)L(\text{head-entity})&space;&plus;&space;\lambda&space;L(\text{tail-entity},&space;\text{relation})" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\dpi{120}&space;L&space;=&space;(1-\lambda)L(\text{head-entity})&space;&plus;&space;\lambda&space;L(\text{tail-entity},&space;\text{relation})" title="L = (1-\lambda)L(\text{head-entity}) + \lambda L(\text{tail-entity}, \text{relation})" /></a>

where <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;\dpi{120}&space;\lambda" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\inline&space;\dpi{120}&space;\lambda" title="\lambda" /></a> is the parameter that controls the trade-off between extracting the right head entities and accurately extracting the tail entities in their corresponding relations. Please refer to the [paper](https://arxiv.org/abs/1905.05529) for more details.

The code for the original model is available at [the official repository](https://github.com/ShannonAI/Entity-Relation-As-Multi-Turn-QA) of the paper.

## Post-processing
The output of the model for each football article is written in a text file where each line contains an entity or a relation prediction. For example:
```
CLU Chelsea
CLU Arsenal
COMP Chelsea Arsenal
```
In order to combine the extracted entities and relations to form the prediction result, we propose some heuristic approaches to filter then convert the output of the system to submission's format. The required fields are completed in the following order: 
1. Teams
2. Score board
3. Score list
4. Card list
5. Substitution list

### Teams
As many extracted entities and relations comprise team names, we propose to set priorities over the order of team name extraction. Of the highest priority is `COMP` relation where both team names may exist. The second priority lies on `SCOP`, `SCOC` and `CARP` where the club is paired with a player, score or card. We choose `CLU` as the lowest priority as a football article may contain several references of a club name (even a random one to make comparison).

To avoid alias or inconsistent occurences of team name, we use longest common sequence algorithm (lcs) to check and keep the longer name.


### Score board
We include all goalscore information from the `SCOP`, `SCOC` and `SCO` extracted by our model. With `SCOP` relation, we group the players by their corresponding team and assume the team score is its number of players. We then continue to extract score information from `SCOC`, and only use `SCO` to handle draw cases. 

### Score list
We include all goalscore information from the `SCOT` and `SCOP` extracted by our model. We use the `SCOT` to fill in the `player_name` and `time` fields, then use the `SCOP` to map the `player_name` to their `team` if this information is available, otherwise, we set `team` to an empty string. We also include all remaining `SCOP` players with their club information that do not appear in `SCOT` relation in our final score list. Note that we do not take into account the standalone PSC and TSC entities as doing so jeopadizes our performance on the public test set.

### Card list
The card list is constructed from the information in the `CART` and `CARP` relations. We follow the same procedure as that for the score list. 

### Substitution list 
To create the substitution list, we iterate through all the `SUBP(PSI, PSO)` in the output file to get `player_in` and `player_out` information, and use the `SUBT` relation to pull out the corresponding `time` for the substitution (set `time` to an empty string if this information is not available). We then append the list with all the `in_player` that have not been included with the substitution `time` from the `SUBT`. We again do not consider using the standalone entities `PSI`, `PSO` and `TSI` when constructing the list.

# Code usage
Firstly, clone our this repository
## Install Requirements
`pip install -r requirements.txt`

## Preprocessing
Put train data into ./data/raw
Go to scripts folder `cd scripts`
Run command `sh prepare_zalo.sh`

## Training
Go to scripts folder `cd scripts`
Run command `sh train_zalo.sh`
After run, model is saved in ./checkpoint 

## Inference
If you want to only predict, please download my [docker](https://drive.google.com/file/d/14TUipw86ZQEyATvqNa6Ew9SCH1Ru79Xl/view?usp=sharing)
Load image `docker load < nkt_image.tar.gz`
Run command `docker run –v [path to test data]:/data –v [path to result folder]:/result nkt_image:final /bin/bash
/model/predict.sh`






