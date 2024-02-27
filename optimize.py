
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
max_budget = 700 

def get_players_in_position(dataframe, position_key):
    position_filter = dataframe['position'] == position_key
    filtered_dataframe = dataframe[position_filter]

    
    player_names = filtered_dataframe['name'].tolist()

    return player_names

for position in ['DEF', 'MID', 'FWD', 'GK']:
    
    players_in_position = get_players_in_position(data, position)
    
    
    if position == 'DEF':
        constant_value = -num_defenders
    elif position == 'MID':
        constant_value = -num_midfielders
    elif position == 'FWD':
        constant_value = -num_forwards
    elif position == 'GK':
        constant_value = -num_keeper
    else:
        
        raise ValueError(f"Unexpected position value: {position}")

    # constraint_dict = {player: 1 for player in players_in_position}
    constraint_dict = [(player, 1) for player in players_in_position]

    # print(constraint_dict)
    bqm.add_linear_equality_constraint(
        constraint_dict,
        constant=constant_value,
        lagrange_multiplier=5  
    )
"""
Add constraints for total team value(points)
"""
#bqm.add_linear_inequality_constraint(
    # {player['name']: player['value'] for index, player in data.iterrows()}
 #   [(player['name'], player['total_points']) for index, player in data.iterrows()],
  
  #  lagrange_multiplier=10, 
   # label='points_constraint'
#)

# Add budget constraint
player_values = [(player['name'], player['value']) for index, player in data.iterrows()]  # Create a dictionary of player values
bqm.add_linear_inequality_constraint(
    player_values,  # Use player values for the constraint
    constant=-max_budget,
    lagrange_multiplier=10, 
    label='budget_constraint'
)
api_token = 'DEV-257ed80ce0a221025ddaa4b7acb440d9978e1f42'
sampler = EmbeddingComposite(DWaveSampler(token= api_token))
results = sampler.sample(bqm)
#print(results.first.sample)
selected_players = [player for player in results.first.sample if results.first.sample[player] == 1]
positions = list(data[data["name"].isin(selected_players)]["position"])
for i in range(len(selected_players)):
    position_use = data[data["name"]==selected_players[i]]["position"]
    print(selected_players[i], position_use)
print("Selected Players:", selected_players)
#print("Total Points:", -results.first.energy)

