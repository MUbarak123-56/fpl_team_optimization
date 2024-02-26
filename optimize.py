


# from dwave.system import DWaveSampler, EmbeddingComposite
# import dimod
# import pandas as pd

# # Initialize Binary Quadratic Model
# bqm = dimod.BinaryQuadraticModel('BINARY')

# # Load player data
# data = pd.read_excel("data.xlsx")

# # Add variables for each player, weighted by negative total points
# for index, player in data.iterrows():
#     bqm.add_variable(player['name'], -player['total_points'])

# # Constraints for team formation (e.g., 4-3-3)
# num_defenders = 4
# num_midfielders = 3
# num_forwards = 3

# # Constraint for total team value
# max_team_value = 1000  # Example value

# # Add position constraints
# for position in ['Defender', 'Midfielder', 'Forward']:
#     players_in_position = data[data['position'] == position]['name']
#     bqm.add_linear_equality_constraint(
#         {player: 1 for player in players_in_position},
#         constant=-num_defenders if position == 'Defender' else -num_midfielders if position == 'Midfielder' else -num_forwards,
#         lagrange_multiplier=10  # Example value for Lagrange multiplier,
        
#     )

# # Add constraint for total team value
# bqm.add_linear_inequality_constraint(
#     {player['name']: player['value'] for index, player in data.iterrows()},
#     constant=-max_team_value,
#     lagrange_multiplier=10,  # Example value for Lagrange multiplier
#     label='team_value_constraint'
# )

# #add constraint for budget

# # Continue with sampler setup and problem solving as before

# # Define constraints here (e.g., number of players in each position, total team value)

# # Setup D-Wave sampler
# # sampler = EmbeddingComposite(DWaveSampler())

# # # Solve the problem using the D-Wave sampler
# # results = sampler.sample(bqm)

# # Process and display results (e.g., selected players for optimal team)

from dwave.system import DWaveSampler, EmbeddingComposite
import dimod
import pandas as pd

# Initialize Binary Quadratic Model
bqm = dimod.BinaryQuadraticModel('BINARY')

# Load player data
data = pd.read_excel("data.xlsx")

# Add variables for each player, weighted by negative total points
for index, player in data.iterrows():
    bqm.add_variable(player['name'], -player['total_points'])

# Constraints for team formation (e.g., 4-3-3)
num_keeper = 1
num_defenders = 4
num_midfielders = 3
num_forwards = 3

# Constraint for total team value
max_team_value = 1000  # Example value

#Add position constraints
# for position in ['DEF', 'MID', 'FWD']:
#     players_in_position = data[data['position'] == position]['name'].tolist()  # Ensure this is a list of player names
#     print(players_in_position)
#     constant_value = -num_defenders if position == 'DEF' else -num_midfielders if position == 'MID' else -num_forwards if position == 'FWD' else -num_keeper
#     player_dict = {player: 1 for player in players_in_position}  # Construct the dictionary outside the method call
    

#     bqm.add_linear_equality_constraint(
#         player_dict,
#         constant=constant_value,
#         lagrange_multiplier=10  # Example value for Lagrange multiplier
#     )
def get_players_in_position(dataframe, position_key):
    """
    Filters players in the given position and returns their names as a list.

    :param dataframe: The pandas DataFrame containing player data.
    :param position_key: The position to filter players by (e.g., 'DEF', 'MID', 'FWD').
    :return: A list of player names in the specified position.
    """
    # Filter the DataFrame for rows where the 'position' column matches the specified position
    position_filter = dataframe['position'] == position_key
    filtered_dataframe = dataframe[position_filter]

    # Extract the 'name' column from the filtered DataFrame and convert it to a list
    player_names = filtered_dataframe['name'].tolist()

    return player_names

# print(get_players_in_position(data, 'GK'))
# Define a more readable approach to filter players by position and collect their names
def get_players_in_position(dataframe, position_key):
    """
    Filters players in the given position and returns their names as a list.

    :param dataframe: The pandas DataFrame containing player data.
    :param position_key: The position to filter players by (e.g., 'DEF', 'MID', 'FWD').
    :return: A list of player names in the specified position.
    """
    # Filter the DataFrame for rows where the 'position' column matches the specified position
    position_filter = dataframe['position'] == position_key
    filtered_dataframe = dataframe[position_filter]

    # Extract the 'name' column from the filtered DataFrame and convert it to a list
    player_names = filtered_dataframe['name'].tolist()

    return player_names

# Use the defined function in the loop to set up constraints
for position in ['DEF', 'MID', 'FWD', 'GK']:
    # Call the function to get a list of player names in the current position
    players_in_position = get_players_in_position(data, position)
    
    #Determine the constant value based on the position
    if position == 'DEF':
        constant_value = -num_defenders
    elif position == 'MID':
        constant_value = -num_midfielders
    elif position == 'FWD':
        constant_value = -num_forwards
    elif position == 'GK':
        constant_value = -num_keeper
    else:
        # Handle unexpected position values
        raise ValueError(f"Unexpected position value: {position}")

    #Construct the constraint dictionary
    constraint_dict = {player: 1 for player in players_in_position}
    print(constraint_dict)
   

    #Add the linear equality constraint to the binary quadratic model
    bqm.add_linear_equality_constraint(
        constraint_dict,
        constant=constant_value,
        lagrange_multiplier=10  # Example value for Lagrange multiplier
    )



