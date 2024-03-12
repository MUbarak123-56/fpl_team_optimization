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

extract_data = pd.read_csv("https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2023-24/gws/merged_gw.csv")

def accumulated(df):
    # Add a column 'n' with all values set to 1
    df['n'] = 1
    
    # Group by 'name' and 'team'
    grouped = df.groupby(['name', 'team'])
    
    # Define the columns to apply the cumulative sum and then subtract the original value
    cols_to_accumulate = ['goals_scored', 'assists', 'ict_index', 'goals_conceded', 'minutes', 'own_goals', 'bps', 'clean_sheets', 'bonus']
    
    # Apply the cumulative sum and subtraction
    for col in cols_to_accumulate:
        df[col + '_cum'] = grouped[col].cumsum() - df[col]
    
    # For 'total_points', just the cumulative sum is needed
    df['total_points_cum'] = grouped['total_points'].cumsum()
    
    # Select the desired columns
    df = df[['name', 'team', 'position', 'value', 'goals_scored_cum', 'assists_cum', 'ict_index_cum', 'goals_conceded_cum', 'minutes_cum', 'own_goals_cum', 'total_points_cum', 'bps_cum', 'bonus_cum', 'clean_sheets_cum', 'GW', 'kickoff_time']]
    
    # Filter rows where 'ict_index_cum' > 0
    #df = df[df['ict_index_cum'] > 0]
    
    # Drop the temporary 'n' column
    #df.drop(columns=['n'], inplace=True)
    
    # Rename the accumulated columns back to their original names for clarity
    df.rename(columns={col + '_cum': col for col in cols_to_accumulate}, inplace=True)
    df.rename(columns={'total_points_cum': 'total_points'}, inplace=True)
    
    return df

cumulative_df = accumulated(extract_data)

cumulative_df["date"] = pd.to_datetime(cumulative_df["kickoff_time"]).dt.date
cumulative_df.index = cumulative_df["date"]
cumulative_df = cumulative_df.sort_index()
date_range = pd.date_range(start=cumulative_df.index.min(), end = cumulative_df.index.max())
cumulative_df["name_team"] = cumulative_df["name"] + "_" + cumulative_df["team"]
new_df = pd.DataFrame()
for combo in list(cumulative_df["name_team"].unique()):
    new_data = cumulative_df[cumulative_df["name_team"] == combo]
    post = new_data["position"].unique()[0]
    name, team = combo.split("_")[0], combo.split("_")[1]
    new_data_reindexed = new_data.reindex(date_range)
    new_data_reindexed["name"] = name
    new_data_reindexed["team"] = team
    new_data_reindexed["position"] = post
    new_data_reindexed["date"] = new_data_reindexed.index
    new_data_reindexed = new_data_reindexed.ffill(axis=0)
    new_data_reindexed = new_data_reindexed.dropna()
    new_data_reindexed = new_data_reindexed.reset_index(drop=True)
    
    new_df = pd.concat([new_df, new_data_reindexed], axis = 0).reset_index(drop=True)
    
latest_df = new_df[new_df["date"]==max(new_df["date"])][["name", "team", "total_points", "date", "position", "value", "GW"]].reset_index(drop=True)

gk = latest_df[latest_df["position"]=="GK"].sort_values("total_points", ascending=False).reset_index(drop=True).head(5)
defenders = latest_df[latest_df["position"]=="DEF"].sort_values("total_points", ascending=False).reset_index(drop=True).head(10)
midfielders = latest_df[latest_df["position"]=="MID"].sort_values("total_points", ascending=False).reset_index(drop=True).head(10)
forwards = latest_df[latest_df["position"]=="FWD"].sort_values("total_points", ascending=False).reset_index(drop=True).head(10)
data = pd.concat([gk, defenders, midfielders, forwards], axis = 0).sort_values("position", ascending=False).reset_index(drop=True)
gw = max(data["GW"])
columns = ["name", "position", "value", "total_points"]
data = data[columns]
data["value"] = data["value"]/10
df_use = data.sort_values("position").reset_index(drop=True)

defense_list_index = list(df_use[df_use["position"]=="DEF"].index)
forward_list_index = list(df_use[df_use["position"]=="FWD"].index)
gk_list_index = list(df_use[df_use["position"]=="GK"].index)
midfield_list_index = list(df_use[df_use["position"]=="MID"].index)

for i in range(len(df_use)):
    df_use.loc[i, "variable"] = "x[" + str(i) + "]"
df_use
columns = ["variable","name", "position", "value", "total_points"]
total_points = df_use["total_points"].to_list()
value = df_use["value"].to_list()
df_use = df_use[columns]
lagrange = 1716
lagrange_budget = 1551
num_var = 38
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
    midfield = get_input("How many midfielders do you want? Choose a number between 2 and 5: ", 2, 5)
    forward = get_input("How many forwards do you want? Choose a number between 1 and 4: ", 1, 4)

    return defense, midfield, forward

defense, midfield, forward = handle_inputs()
summation = defense + midfield + forward

while summation != 10:
    print("The total number of players must be 10. Please try again.")
    defense, midfield, forward = handle_inputs()
    summation = defense + midfield + forward

print(f"Team configuration: {defense} Defenders, {midfield} Midfielders, {forward} Forwards")

x = Array.create('x', shape=num_var, vartype='BINARY')
s = Array.create('s', shape=slack_num, vartype='BINARY')

# objective function
h = sum(n * x for x, n in zip(x, total_points))

# constraints
c1 = lagrange * Constraint((sum(x[n] for n in range(0, num_var)) - 11)**2,
                                                label='11 players team')
c2 = lagrange * Constraint((sum(x[n] for n in range(min(defense_list_index), max(defense_list_index)+1))-defense)**2,
                                                label=str(defense) + " defenders")
c3 = lagrange * Constraint((sum(x[n] for n in range(min(forward_list_index), max(forward_list_index)+1))-forward)**2,
                                                label=str(forward) + " forwards")
c4 = lagrange * Constraint((sum(x[n] for n in range(min(gk_list_index), max(gk_list_index)+1))-1)**2,
                                                label= "1 keeper")
c5 = lagrange * Constraint((sum(x[n] for n in range(min(midfield_list_index), max(midfield_list_index)+1))-midfield)**2,
                                                label=str(midfield) + " midfielders")
c6 = lagrange_budget * Constraint((sum(n * x for x, n in zip(x, value)) + s[0] -70)**2,
                                                              label="budget")
H = -1 * h + c1 + c2 + c3 + c4 + c5 + c6

model = H.compile()
qubo, offset = model.to_qubo()
bqm = model.to_bqm()

sampler = LeapHybridSampler()
sampleset = sampler.sample(bqm,
                            label="FPL line-up optimization")

decoded_samples = model.decode_sampleset(sampleset)
best_sample = min(decoded_samples, key=lambda x: x.energy)

print(best_sample.constraints())

lineup_df = pd.DataFrame(best_sample.sample.items())
lineup_df.columns = ['variable', 'selected']
lineup_df = lineup_df[(lineup_df['variable'].str.startswith(
    'x', na=False)) & (lineup_df['selected'] == 1)]
lineup_df = df_use.merge(lineup_df, on=['variable'])

gk = lineup_df[lineup_df["position"] == "GK"]
defense_list = lineup_df[lineup_df["position"] == "DEF"]
midfield_list = lineup_df[lineup_df["position"] == "MID"]
forward_list = lineup_df[lineup_df["position"] == "FWD"]
ordered_lineup_df = pd.concat([gk, defense_list, midfield_list, forward_list], axis=0).reset_index(drop=True)
ordered_lineup_df = ordered_lineup_df[["name", "position", "value", "total_points"]]
print("After game week ", gw, ", the optimal ", defense, "-", midfield, "-", forward, "starting line-up is:")
print(ordered_lineup_df)
print("Total sum of points: ", ordered_lineup_df['total_points'].sum())
print("Total budget: ", ordered_lineup_df['value'].sum())
