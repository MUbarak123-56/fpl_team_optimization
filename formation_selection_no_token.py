import pandas as pd
from pyqubo import Constraint, Array
import neal
from dwave.system import DWaveSampler, EmbeddingComposite, LeapHybridBQMSampler,  LeapHybridSampler
import dimod
import os
from dotenv import load_dotenv

data = pd.read_excel("data.xlsx")
columns = ["name", "position", "value", "total_points"]
data = data[columns]
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
# Decode samples and select the best one
decoded_samples = model.decode_sampleset(sampleset)
best_sample = min(decoded_samples, key=lambda x: x.energy)

# Print to see if constraints are fulfilled
print(best_sample.constraints())
# Print results for best line-up
lineup_df = pd.DataFrame(best_sample.sample.items())
lineup_df.columns = ['variable', 'selected']
lineup_df = lineup_df[(lineup_df['variable'].str.startswith(
    'x', na=False)) & (lineup_df['selected'] == 1)]
lineup_df = df_use.merge(lineup_df, on=['variable'])

# Print line-up and maximized energy for the objective function
gk = lineup_df[lineup_df["position"] == "GK"]
defense_list = lineup_df[lineup_df["position"] == "DEF"]
midfield_list = lineup_df[lineup_df["position"] == "MID"]
forward_list = lineup_df[lineup_df["position"] == "FWD"]
ordered_lineup_df = pd.concat([gk, defense_list, midfield_list, forward_list], axis=0).reset_index(drop=True)
ordered_lineup_df = ordered_lineup_df[["name", "position", "value", "total_points"]]
print(ordered_lineup_df)
print("Total sum of points: ", ordered_lineup_df['total_points'].sum())
print("Total budget: ", ordered_lineup_df['value'].sum())
