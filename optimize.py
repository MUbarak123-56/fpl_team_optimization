
from dwave.system import DWaveSampler, EmbeddingComposite
import dimod
import pandas as pd

bqm = dimod.BinaryQuadraticModel('BINARY')


data = pd.read_excel("data.xlsx")


for index, player in data.iterrows():
    bqm.add_variable(player['name'], -player['total_points'])


num_keeper = 1
num_defenders = 4
num_midfielders = 3
num_forwards = 3


#max_points = 800 
max_budget = 550

def get_players_in_position(dataframe, position_key):
    position_filter = dataframe['position'] == position_key
    filtered_dataframe = dataframe[position_filter]

    
    player_names = filtered_dataframe['name'].tolist()

    return player_names

    
def_in_position = get_players_in_position(data, 'DEF')
mid_in_position = get_players_in_position(data, 'MID')
fwd_in_position = get_players_in_position(data, 'FWD')
gk_in_position = get_players_in_position(data, 'GK')


def_constraint = [(player, 1) for player in def_in_position]
mid_constraint= [(player, 1) for player in mid_in_position]
fwd_constraint = [(player, 1) for player in fwd_in_position]
gk_constraint = [(player, 1) for player in gk_in_position]

# print(constraint_dict)
bqm.add_linear_equality_constraint(
    def_constraint,
    constant= -4,
    lagrange_multiplier=4
)

bqm.add_linear_equality_constraint(
    mid_constraint,
    constant= -3,
    lagrange_multiplier=3 
)

bqm.add_linear_equality_constraint(
    fwd_constraint,
    constant= -3,
    lagrange_multiplier=3
)
bqm.add_linear_equality_constraint(
    gk_constraint,
    constant= -1,
    lagrange_multiplier=1
)



# Add budget constraint
player_values = [(player['name'], player['value']) for index, player in data.iterrows()]  # Create a dictionary of player values
bqm.add_linear_inequality_constraint(
    player_values,  # Use player values for the constraint
    constant=-max_budget,
    lagrange_multiplier=750, 
    label='budget_constraint'
)
api_token = 'DEV-257ed80ce0a221025ddaa4b7acb440d9978e1f42'
sampler = EmbeddingComposite(DWaveSampler(token= api_token))
results = sampler.sample(bqm)
selected_players = [player for player in results.first.sample if results.first.sample[player] == 1]
#positions = list(data[data["name"].isin(selected_players)]["position"])
position_list = []
for i in range(len(selected_players)):
    position_use = str(data[data["name"]==selected_players[i]]["position"][0])
    if (position_use == "DEF") or (position_use == "MID") or (position_use == "FWD") or (position_use == "GK"):
        print(selected_players[i], position_use)
        position_list.append(position_use)

from collections import Counter
print(Counter(position_list))
#print("Selected Players:", selected_players)
#print("Total Points:", -results.first.energy)

#add an objective function
#troubleshoot multiple keeper problem

