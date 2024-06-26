import pandas as pd
from pyqubo import Constraint, Array
import neal
from dwave.system import DWaveSampler, EmbeddingComposite, LeapHybridBQMSampler,  LeapHybridSampler
import dimod
import os
from dotenv import load_dotenv
import numpy as np
import warnings
warnings.filterwarnings('ignore')

#load_dotenv()
#token_use = os.getenv("API_TOKEN")

data = pd.read_excel("use_data.xlsx")
gw = max(data["GW"])
columns = ["name", "position", "value", "total_points", "team", "points_per_game"]
data = data[columns]
data["value"] = data["value"]/10
df_use = data.sort_values("position").reset_index(drop=True)

defense_list_index = list(df_use[df_use["position"]=="DEF"].index)
forward_list_index = list(df_use[df_use["position"]=="FWD"].index)
gk_list_index = list(df_use[df_use["position"]=="GK"].index)
midfield_list_index = list(df_use[df_use["position"]=="MID"].index)

for i in range(len(df_use)):
    df_use.loc[i, "variable"] = "x[" + str(i) + "]"
    
columns = ["variable","name", "position", "value", "total_points", "team", "points_per_game"]
team_list = list(df_use["team"].unique())
total_points = df_use["points_per_game"].to_list()
value = df_use["value"].to_list()
df_use = df_use[columns]

lagrange = max(df_use["points_per_game"])*15
# lagrange_def = max(df_use["points_per_game"])*5
# lagrange_mid = max(df_use["points_per_game"])*5
# lagrange_fwd = max(df_use["points_per_game"])*3
# lagrange_gk = max(df_use["points_per_game"])*2
lagrange_budget = max(df_use["value"])*15
lagrange_team = max(df_use["points_per_game"])*3
num_var = len(df_use)
slack_num = 1

def get_input(prompt, min_val, max_val):
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Please choose a number between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def handle_inputs():
    defense = get_input("How many defenders do you want? Choose a number between 3 and 5: ", 3, 5)
    midfield = get_input("How many midfielders do you want? Choose a number between 3 and 5: ", 3, 5)
    forward = get_input("How many forwards do you want? Choose a number between 1 and 3: ", 1, 3)

    return defense, midfield, forward

defense, midfield, forward = handle_inputs()
summation = defense + midfield + forward

while summation != 10:
    print("The total number of players must be 10. Please try again.")
    defense, midfield, forward = handle_inputs()
    summation = defense + midfield + forward

print(f"Team configuration: {defense} Defenders, {midfield} Midfielders, {forward} Forwards")

x = Array.create('x', shape=num_var, vartype='BINARY')
s = Array.create('s', shape=slack_num + len(df_use["team"].unique()), vartype='BINARY')

# objective function
h = sum(n * x for x, n in zip(x, total_points))

# constraints
c1 = lagrange * Constraint((sum(x[n] for n in range(0, num_var)) - 15)**2,
                                                label='15 players squad')
c2 = lagrange * Constraint((sum(x[n] for n in range(min(defense_list_index), max(defense_list_index)+1))-5)**2,
                                                label=str(5) + " defenders")
c3 = lagrange * Constraint((sum(x[n] for n in range(min(forward_list_index), max(forward_list_index)+1))-3)**2,
                                                label=str(3) + " forwards")
c4 = lagrange * Constraint((sum(x[n] for n in range(min(gk_list_index), max(gk_list_index)+1))-2)**2,
                                                label= "2 keepers")
c5 = lagrange * Constraint((sum(x[n] for n in range(min(midfield_list_index), max(midfield_list_index)+1))-5)**2,
                                                label=str(5) + " midfielders")
c6 = lagrange_budget * Constraint((sum(n * x for x, n in zip(x, value)) + s[0] -100)**2,
                                                              label="budget")

c7 = 0

for i in range(len(team_list)):
    use_index =list(df_use[df_use["team"]==team_list[i]].index)
    c7 += lagrange_team * Constraint((sum(x[n] for n in use_index) + s[i+1] - 3)**2, label = str(team_list[i]) + " selection")
    
H = -1 * h + c1 + c2 + c3 + c4 + c5 + c6 + c7

model = H.compile()
bqm = model.to_bqm()

#api_token = token_use
sampler = LeapHybridSampler()
sampleset = sampler.sample(bqm, label="FPL Team optimization")

decoded_samples = model.decode_sampleset(sampleset)
best_sample = min(decoded_samples, key=lambda x: x.energy)

team_df = pd.DataFrame(best_sample.sample.items())
team_df.columns = ['variable', 'selected']
team_df = team_df[(team_df['variable'].str.startswith(
    'x', na=False)) & (team_df['selected'] == 1)]
team_df = df_use.merge(team_df, on=['variable'])

# Obtain starting line-up
gk = team_df[team_df["position"] == "GK"].sort_values("points_per_game", ascending=False).head(1)
defense_list = team_df[team_df["position"] == "DEF"].sort_values("points_per_game", ascending=False).head(defense)
midfield_list = team_df[team_df["position"] == "MID"].sort_values("points_per_game", ascending=False).head(midfield)
attack_list = team_df[team_df["position"] == "FWD"].sort_values("points_per_game", ascending=False).head(forward)
start_lineup_df = pd.concat([gk, defense_list, midfield_list, attack_list], axis=0).reset_index(drop=True)
start_lineup_df = start_lineup_df[["name", "team", "position", "value", "total_points", "points_per_game"]]

# Obtain bench players
gk = team_df[team_df["position"] == "GK"].sort_values("points_per_game", ascending=False).tail(1)
defense_list = team_df[team_df["position"] == "DEF"].sort_values("points_per_game", ascending=False).tail(5-defense)
midfield_list = team_df[team_df["position"] == "MID"].sort_values("points_per_game", ascending=False).tail(5-midfield)
attack_list = team_df[team_df["position"] == "FWD"].sort_values("points_per_game", ascending=False).tail(3-forward)
bench_lineup_df = pd.concat([gk, defense_list, midfield_list, attack_list], axis=0).reset_index(drop=True)
bench_lineup_df = bench_lineup_df[["name", "team", "position", "value", "total_points", "points_per_game"]]

print("At Gameweek ", gw, ", the optimal squad would look like:\n")
print("Starting Lineup")
print(start_lineup_df)
print("\n\n")
print("Bench")
print(bench_lineup_df)
print("Total starting line up sum of FPL points per game: ", start_lineup_df["points_per_game"].sum())
print("Total budget: ", team_df['value'].sum())
