import streamlit as st
from pyqubo import Constraint, Array
import neal
from dwave.system import DWaveSampler, EmbeddingComposite, LeapHybridBQMSampler,  LeapHybridSampler
import dimod
import os
from dotenv import load_dotenv
import pandas as pd
import time

st.set_page_config(page_title = "FPL Line Up Selector", page_icon="⚽")

st.header("FPL Line Up Selector ⚽")

st.subheader("Welcome to the FPL Line Up Selector App")
st.write("""The purpose of this app is to assist FPL fans to select the optimal starting line-up according to data collected from Gameweek 1 to Gameweek 23 of the 2023/24 season. 
            The data collected reflects the top 39 highest rated players so far this season in terms of FPL points accumulated over 23 game weeks. By leveraging D-Wave's LeapHybridSolver,
            you will be able to view what the optimal starting line-up would be based on your desired formation. This line-up also takes budget into account. The budget for each starting line-up is 
            expected to be 1000, which is the same as what FPL website typically sets its budget as. Hence, you will be constrained to a starting line-up whose value will not exceed 1000.
            """)
# loading in the D-Wave Token
load_dotenv()
token_use = os.getenv("API_TOKEN")

# Loading in the FPL data set
data = pd.read_excel("data.xlsx")
columns = ["name", "position", "value", "total_points"]
data = data[columns]
df_use = data.sort_values("position").reset_index(drop=True)
for i in range(len(df_use)):
    df_use.loc[i, "variable"] = "x[" + str(i) + "]"
    
columns = ["variable","name", "position", "value", "total_points"]
total_points = df_use["total_points"].to_list()
value = df_use["value"].to_list()
df_use = df_use[columns]
lagrange = 1716
lagrange_budget = 1551
num_var = 38
slack_num = 1

defense = st.number_input("How many defenders do you want?", min_value=3, max_value=5, value = 4)
mid_use = (10 - defense) - 1
midfield = st.number_input("How many midfielders do you want?", min_value=2, max_value=mid_use, value = 4)
forward_use = 10 - (defense + midfield)
forward = st.number_input("How many forwards do you want?", min_value=forward_use, max_value=forward_use)
selection = defense + midfield + forward

st.write("Team configuration: ", defense, "-", midfield, "-", forward)

with st.spinner('Please wait...Line up is being selected'):
    time.sleep(5)
    x = Array.create('x', shape=num_var, vartype='BINARY')
    s = Array.create('s', shape=slack_num, vartype='BINARY')
    # objective function
    h = sum(n * x for x, n in zip(x, total_points))
    C1 = lagrange * Constraint((sum(x[n] for n in range(0, num_var)) - 11)**2,
                        label='11 players team')
    C2 = lagrange * Constraint((sum(x[n] for n in range(0, 10))-defense)**2,
                        label=str(defense) + " defenders")
    C3 = lagrange * Constraint((sum(x[n] for n in range(10, 21))-forward)**2,
                        label=str(forward) + " forwards")
    C4 = lagrange * Constraint((sum(x[n] for n in range(21, 28))-1)**2,
                        label= "1 keeper")
    C5 = lagrange * Constraint((sum(x[n] for n in range(28,  38))-midfield)**2,
                        label=str(midfield) + " midfielders")
    C6 = lagrange_budget * Constraint((sum(n * x for x, n in zip(x, value)) + s[0] -1000)**2,
                                      label="budget")
    H = -1 * h + C1 + C2 + C3 + C4 + C5 + C6
    model = H.compile()
    qubo, offset = model.to_qubo()
    bqm = model.to_bqm()
    
    # Uncomment to solve problem by simulation
    # sa = neal.SimulatedAnnealingSampler()
    # sampleset = sa.sample(bqm, num_reads=10000)
    
    # Solve problem with QPU
    #api_token = 'DEV-257ed80ce0a221025ddaa4b7acb440d9978e1f42'
    sampler = LeapHybridSampler(token= token_use)
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
    st.dataframe(ordered_lineup_df)
    st.write("Total sum of points: ", ordered_lineup_df['total_points'].sum())
    st.write("Total budget: ", ordered_lineup_df['value'].sum())
