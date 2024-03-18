import streamlit as st
from pyqubo import Constraint, Array
import neal
from dwave.system import DWaveSampler, EmbeddingComposite, LeapHybridBQMSampler,  LeapHybridSampler
import dimod
import os
from dotenv import load_dotenv
import pandas as pd
import time
import numpy as np
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title = "FPL Line Up Optimizer", page_icon="⚽")

st.header("FPL Line Up Optimizer ⚽")

st.subheader("Welcome to the FPL Line Up Optimizer App")
st.write("""The purpose of this app is to assist FPL fans to select the optimal starting line-up according to data collected from Gameweek 1 to the most recent gameweek of the 2023/24 season. 
            The data collected reflects the top 35 highest rated players (5 goalkeepers, 10 defenders, 10 midfielders and 10 forwards) so far this season in terms of FPL points accumulated over all the games. By leveraging D-Wave's LeapHybridSolver,
            you will be able to view what the optimal starting line-up would be based on your desired formation. You can sign up for D-Wave Leap [here](https://cloud.dwavesys.com/leap/) and obtain your solver API token. 
            Once you have obtained it, insert it into the D-Wave Solver API token in the sidebar.
            This line-up also takes budget into account. The budget for each starting line-up is expected to be 70. Hence, you will be constrained to a starting line-up whose total value will not exceed 70.
            70 was selected because anything beyond 70 typically selects more than 11 players.
            The regular FPL budget is 100 which selects the starting 11 players including 4 substitutes.
            """)
# loading in the D-Wave Token
#load_dotenv()
#token_use = os.getenv("API_TOKEN")

# Loading in the FPL data set

data = pd.read_excel("data.xlsx")
gw = max(data["GW"])

columns = ["name", "position", "value", "total_points"]
data = data[columns]
data["value"] = data["value"]/10
df_use = data.sort_values("position").reset_index(drop=True)
for i in range(len(df_use)):
    df_use.loc[i, "variable"] = "x[" + str(i) + "]"

defense_list_index = list(df_use[df_use["position"]=="DEF"].index)
forward_list_index = list(df_use[df_use["position"]=="FWD"].index)
gk_list_index = list(df_use[df_use["position"]=="GK"].index)
midfield_list_index = list(df_use[df_use["position"]=="MID"].index)
    
columns = ["variable","name", "position", "value", "total_points"]
total_points = df_use["total_points"].to_list()
value = df_use["value"].to_list()
df_use = df_use[columns]
lagrange = 1716
lagrange_budget = 1551
num_var = 38
slack_num = 1

st.markdown("<h4 style='text-align: left; color: white;'>Formation Selection</h4>", unsafe_allow_html=True)
st.write("Toggle with the following widgets to set your formation. You can play around with the defense and midfield but not attack because your formation must have exactly 11 players (including the goalkeeper).")

defense = st.number_input("How many defenders do you want?", min_value=3, max_value=5, value = 4)
mid_use = (10 - defense) - 1
midfield = st.number_input("How many midfielders do you want?", min_value=2, max_value=mid_use, value = 4)
forward_use = 10 - (defense + midfield)
forward = st.number_input("How many forwards do you want?", min_value=forward_use, max_value=forward_use)

st.write("Team configuration: ", defense, "-", midfield, "-", forward)

#st.write('**D-Wave Token Insertion**')
st.markdown("<h4 style='text-align: left; color: white;'>D-Wave Token Insertion</h4>", unsafe_allow_html=True)
st.write("Go to this [webpage](https://cloud.dwavesys.com/leap/) and sign up for D-Wave Leap to obtain your token.")
if 'API_TOKEN' in st.secrets:
            st.success('API key already provided!', icon='✅')
            api_key = st.secrets['API_TOKEN']
else:
            api_key = st.text_input('Enter D-Wave Solver API token:', type='password')
            if not (api_key).startswith('DEV') or len(api_key) != 44:
                        st.warning('Please enter your credentials!', icon='⚠️') 
            else:
                        st.success('Your API token has been received. Now optimization will be conducted.', icon='👉')

                        with st.spinner('Please wait...Line up is being selected'):
                            time.sleep(5)
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
                            
                            sampler = LeapHybridSampler(token= api_key)
                            sampleset = sampler.sample(bqm,
                                                        label="FPL line-up optimization")
                            
                            decoded_samples = model.decode_sampleset(sampleset)
                            best_sample = min(decoded_samples, key=lambda x: x.energy)
                            
                            
                            #print(best_sample.constraints())
                            
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

                            line_up = ordered_lineup_df
                            gk_names = line_up[line_up["position"]=="GK"]["name"].to_list()
                            def_names = line_up[line_up["position"]=="DEF"]["name"].to_list()
                            mid_names = line_up[line_up["position"]=="MID"]["name"].to_list()
                            fwd_names = line_up[line_up["position"]=="FWD"]["name"].to_list()

                                    
                            st.write("After game week ", gw, ", the optimal ", defense, "-", midfield, "-", forward, "starting line-up would look like:")
                            st.dataframe(ordered_lineup_df)
                            st.write("Total sum of points: ", ordered_lineup_df['total_points'].sum())
                            st.write("Total budget: ", round(ordered_lineup_df['value'].sum(), 4))
