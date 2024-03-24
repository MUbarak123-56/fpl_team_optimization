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

st.set_page_config(page_title = "FPL Team of the Season", page_icon="⚽")

st.header("FPL Team of the Season ⚽")

st.subheader("This is the FPL Team of the Season Page")
st.write("""Toggle around with the formation widget to see the Team of the Season for any formation""")
# loading in the D-Wave Token
#load_dotenv()
#token_use = os.getenv("API_TOKEN")

# Loading in the FPL data set

tot_df = pd.read_excel("total_data.xlsx")


gk = tot_df[tot_df["position"]=="GK"].sort_values("total_points", ascending=False).reset_index(drop=True).head(5)
defenders = tot_df[tot_df["position"]=="DEF"].sort_values("total_points", ascending=False).reset_index(drop=True).head(15)
midfielders = tot_df[tot_df["position"]=="MID"].sort_values("total_points", ascending=False).reset_index(drop=True).head(15)
forwards = tot_df[tot_df["position"]=="FWD"].sort_values("total_points", ascending=False).reset_index(drop=True).head(15)

data = pd.concat([gk, defenders, midfielders, forwards], axis = 0).sort_values("position", ascending=False).reset_index(drop=True)

gw = max(data["GW"])
columns = ["name", "position", "value", "total_points", "team", "points_per_game"]
data = data[columns]
data["value"] = data["value"]/10
df_use = data.sort_values("position").reset_index(drop=True)
for i in range(len(df_use)):
    df_use.loc[i, "variable"] = "x[" + str(i) + "]"

defense_list_index = list(df_use[df_use["position"]=="DEF"].index)
forward_list_index = list(df_use[df_use["position"]=="FWD"].index)
gk_list_index = list(df_use[df_use["position"]=="GK"].index)
midfield_list_index = list(df_use[df_use["position"]=="MID"].index)
    
columns = ["variable","name", "position", "value", "total_points", "team", "points_per_game"]
team_list = list(df_use["team"].unique())
total_points = df_use["total_points"].to_list()
value = df_use["value"].to_list()
df_use = df_use[columns]

lagrange = max(df_use["total_points"])*15
lagrange_budget = max(df_use["value"])*15
#lagrange_team = max(df_use["total_points"])*3
num_var = len(df_use)
slack_num = 1

st.markdown("<h4 style='text-align: left; color: white;'>Formation Selection</h4>", unsafe_allow_html=True)
st.write("Toggle with the following widgets to set your formation. You can play around with the defense and midfield but not attack because your formation must have exactly 11 players (including the goalkeeper).")

defense = st.number_input("How many defenders do you want?", min_value=3, max_value=5, value = 4)
mid_use = (10 - defense) - 1
midfield = st.number_input("How many midfielders do you want?", min_value=3, max_value=mid_use, value = 4)
forward_use = 10 - (defense + midfield)
forward = st.number_input("How many forwards do you want?", min_value=forward_use, max_value=forward_use)

st.write("Team configuration: ", defense, "-", midfield, "-", forward)

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def draw_soccer_field():
    """
    Draws a detailed soccer field with a green background, complete middle circle,
    and 18-yard boxes.
    """
    # Create figure
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_facecolor('green')  # Set the background color to green

    # Draw the pitch outline
    plt.plot([0, 0, 200, 200, 0], [0, 100, 100, 0, 0], color="white")

    # Draw the middle line
    plt.plot([100, 100], [0, 100], color="white")

    # Draw the complete middle circle
    center_circle = patches.Circle((100, 50), 9.15, edgecolor="white", facecolor="none")
    #ax.add_patch(center_circle)

    # Draw the D-box arcs
    left_arc = patches.Arc((100, 50), height=36.6, width=18.3*2, angle=0, theta1=270, theta2=90, color="white")
    right_arc = patches.Arc((50*2, 25*2), height=18.3*2, width=18.3*2, angle=0, theta1=90, theta2=270, color="white")
    ax.add_patch(left_arc)
    ax.add_patch(right_arc)

    # Draw the 18-yard boxes
    # Left 18-yard box (from the perspective of the viewer)
    ax.add_patch(patches.Rectangle((0, 15*2), 15*2, 20*2, edgecolor="white", facecolor="none"))
    # Right 18-yard box
    ax.add_patch(patches.Rectangle(((100-15)*2, 15*2), 15*2, 20*2, edgecolor="white", facecolor="none"))

    # Set limits and turn off axis
    plt.xlim(0, 100*2)
    plt.ylim(0, 50*2)
    #plt.axis('off')
    # Remove the tick labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Remove the ticks
    ax.set_xticks([])
    ax.set_yticks([])


    return fig, ax

def plot_formation(line_up, line_up2):
    """
    Plots the given formation on a detailed soccer field.
    """
    fig, ax = draw_soccer_field()
    
    gk_names = line_up[line_up["position"]=="GK"]["name"].to_list()
    def_names = line_up[line_up["position"]=="DEF"]["name"].to_list()
    mid_names = line_up[line_up["position"]=="MID"]["name"].to_list()
    fwd_names = line_up[line_up["position"]=="FWD"]["name"].to_list()\

    gk_points = line_up[line_up["position"]=="GK"]["total_points"].to_list()
    def_points = line_up[line_up["position"]=="DEF"]["total_points"].to_list()
    mid_points = line_up[line_up["position"]=="MID"]["total_points"].to_list()
    fwd_points = line_up[line_up["position"]=="FWD"]["total_points"].to_list()

    gk_values = line_up[line_up["position"]=="GK"]["value"].to_list()
    def_values = line_up[line_up["position"]=="DEF"]["value"].to_list()
    mid_values = line_up[line_up["position"]=="MID"]["value"].to_list()
    fwd_values = line_up[line_up["position"]=="FWD"]["value"].to_list()

    gk_teams = line_up[line_up["position"]=="GK"]["team"].to_list()
    def_teams = line_up[line_up["position"]=="DEF"]["team"].to_list()
    mid_teams = line_up[line_up["position"]=="MID"]["team"].to_list()
    fwd_teams = line_up[line_up["position"]=="FWD"]["team"].to_list()
    
    ax.text(50, 97.5, "Guide = Points per game, Value", color="white", fontsize=7, fontweight="bold")
    ax.text(50, 95, "Total Points per game for Starting line up: " + str(round(line_up["total_points"].sum(),2)) + "; " + "Total Squad Budget: " + str(round(line_up2['value'].sum(), 2)), color="white", fontsize=7, fontweight="bold")
    
    ax.plot(15, 50, 'o', markersize=30, color="black", markeredgecolor="white")  # Player icon
    ax.text(15, 50 - 5, gk_names[0], ha="center", va="top", color="white", fontsize=7, fontweight="bold")  # Player name
    info = str(round(gk_points[0],1)) + ", " + str(gk_values[0])
    ax.text(15, 50 - 7, info, ha="center", va="top", color="white", fontsize=7, fontweight="bold")  
    ax.text(15, 50 - 9, gk_teams[0], ha="center", va="top", color="white", fontsize=7, fontweight="bold")  
    
    def_len = len(def_names)
    def_num = list(np.linspace(0, 100, def_len+2))[1:-1]
    for i in range(len(def_num)):
        ax.plot(50, def_num[i], 'o', markersize=30, color="purple", markeredgecolor="white")  # Player icon
        ax.text(50, def_num[i] - 5, def_names[i], ha="center", va="top", color="white", fontsize=7, fontweight="bold")  # Player name
        info = str(round(def_points[i],1)) + ", " + str(def_values[i])
        ax.text(50, def_num[i] - 7, info, ha="center", va="top", color="white", fontsize=7, fontweight="bold") 
        ax.text(50, def_num[i] - 9, def_teams[i], ha="center", va="top", color="white", fontsize=7, fontweight="bold")  
        
    mid_len = len(mid_names)
    mid_num = list(np.linspace(0, 100, mid_len+2))[1:-1]
    for i in range(len(mid_num)):
        ax.plot(100, mid_num[i], 'o', markersize=30, color="purple", markeredgecolor="white")  # Player icon
        ax.text(100, mid_num[i] - 5, mid_names[i], ha="center", va="top", color="white", fontsize=7, fontweight="bold")  # Player name
        info = str(round(mid_points[i],1)) + ", " + str(mid_values[i])
        ax.text(100, mid_num[i] - 7, info, ha="center", va="top", color="white", fontsize=7, fontweight="bold") 
        ax.text(100, mid_num[i] - 9, mid_teams[i], ha="center", va="top", color="white", fontsize=7, fontweight="bold") 

    fwd_len = len(fwd_names)
    fwd_num = list(np.linspace(0, 100, fwd_len+2))[1:-1]
    for i in range(len(fwd_num)):
        ax.plot(150, fwd_num[i], 'o', markersize=30, color="purple", markeredgecolor="white")  # Player icon
        ax.text(150, fwd_num[i] - 5, fwd_names[i], ha="center", va="top", color="white", fontsize=7, fontweight="bold")  # Player name
        info = str(round(fwd_points[i],1)) + ", " + str(fwd_values[i])
        ax.text(150, fwd_num[i] - 7, info, ha="center", va="top", color="white", fontsize=7, fontweight="bold") 
        ax.text(150, fwd_num[i] - 9, fwd_teams[i], ha="center", va="top", color="white", fontsize=7, fontweight="bold") 

    st.pyplot(fig)

def draw_bench():
    fig, ax = plt.subplots(figsize=(10,2))
    ax.set_facecolor('green')  # Set the background color to green

    # Draw the pitch outline
    plt.plot([0, 0, 200, 200, 0], [0, 20, 20, 0, 0], color="white")

    # Set limits and turn off axis
    plt.xlim(0, 200)
    plt.ylim(0, 20)
    #plt.axis('off')
    # Remove the tick labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Remove the ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    return fig, ax

def plot_bench(bench):
    
    fig, ax = draw_bench()
     
    names=bench["name"].tolist()
    points=bench["total_points"].tolist()
    values=bench["value"].tolist()
    teams=bench["team"].to_list()
            
    #gk_names = bench[bench["position"]=="GK"]["name"].to_list()
    #def_names = bench[bench["position"]=="DEF"]["name"].to_list()
    #mid_names = bench[bench["position"]=="MID"]["name"].to_list()
    #fwd_names = bench[bench["position"]=="FWD"]["name"].to_list()
    
    nums = np.linspace(0, 200, 6)[1:-1]
    ax.plot(nums[0], 12, 'o', markersize=30, color="black", markeredgecolor="white")  # Player icon
    ax.text(nums[0], 10-3, names[0], ha="center", va="top", color="white", fontsize=8, fontweight="bold")
    info=str(round(points[0],1)) + ", " + str(values[0])
    ax.text(nums[0], 10-5, info, ha="center", va="top", color="white", fontsize=8, fontweight="bold")
    ax.text(nums[0], 10-7, teams[0], ha="center", va="top", color="white", fontsize=8, fontweight="bold")
    for i in range(1, len(nums)):
        ax.plot(nums[i], 12, 'o', markersize=30, color="purple", markeredgecolor="white")  # Player icon
        ax.text(nums[i], 10-3, names[i], ha="center", va="top", color="white", fontsize=8, fontweight="bold")
        info=str(round(points[i],1)) + ", " + str(values[i])
        ax.text(nums[i], 10-5, info, ha="center", va="top", color="white", fontsize=8, fontweight="bold")
        ax.text(nums[i], 10-7, teams[i], ha="center", va="top", color="white", fontsize=8, fontweight="bold")
        
    st.pyplot(fig)

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

                        with st.spinner('Please wait..Squad is being selected'):
                            time.sleep(5)
                            x = Array.create('x', shape=num_var, vartype='BINARY')
                            s = Array.create('s', shape=slack_num + len(df_use["team"].unique()), vartype='BINARY')
                            # objective function
                            h = sum(n * x for x, n in zip(x, total_points))
                        
                            # constraints
                            c1 = lagrange * Constraint((sum(x[n] for n in range(0, num_var)) - 15)**2, label='15 players squad')
                            c2 = lagrange * Constraint((sum(x[n] for n in range(min(defense_list_index), max(defense_list_index)+1))-5)**2, label=str(5) + " defenders")
                            c3 = lagrange * Constraint((sum(x[n] for n in range(min(forward_list_index), max(forward_list_index)+1))-3)**2, label=str(3) + " forwards")
                            c4 = lagrange * Constraint((sum(x[n] for n in range(min(gk_list_index), max(gk_list_index)+1))-2)**2, label= "2 keepers")
                            c5 = lagrange * Constraint((sum(x[n] for n in range(min(midfield_list_index), max(midfield_list_index)+1))-5)**2, label=str(5) + " midfielders")
                            #c6 = lagrange_budget * Constraint((sum(n * x for x, n in zip(x, value)) + s[0] -100)**2,label="budget")
                            #c7 = 0
                            #for i in range(len(team_list)):
                             #           use_index =list(df_use[df_use["team"]==team_list[i]].index)
                              #          c7 += lagrange_team * Constraint((sum(x[n] for n in use_index) + s[i+1] - 3)**2, label = str(team_list[i]) + " selection")
                            H = -1 * h + c1 + c2 + c3 + c4 + c5
                        
                            model = H.compile()
                            #qubo, offset = model.to_qubo()
                            bqm = model.to_bqm()
                            
                            sampler = LeapHybridSampler(token= api_key)
                            sampleset = sampler.sample(bqm,
                                                        label="FPL Squad optimization")
                            
                            decoded_samples = model.decode_sampleset(sampleset)
                            best_sample = min(decoded_samples, key=lambda x: x.energy)
                            
                            
                            #print(best_sample.constraints())
                            
                            # Obtain best squad 
                        
                            lineup_df = pd.DataFrame(best_sample.sample.items())
                            lineup_df.columns = ['variable', 'selected']
                            lineup_df = lineup_df[(lineup_df['variable'].str.startswith('x', na=False)) & (lineup_df['selected'] == 1)]
                            lineup_df = df_use.merge(lineup_df, on=['variable'])
                        
                            # Obtain starting line-up
                            gk = lineup_df[lineup_df["position"] == "GK"].sort_values("total_points", ascending=False).head(1)
                            defense_list = lineup_df[lineup_df["position"] == "DEF"].sort_values("total_points", ascending=False).head(defense)
                            midfield_list = lineup_df[lineup_df["position"] == "MID"].sort_values("total_points", ascending=False).head(midfield)
                            attack_list = lineup_df[lineup_df["position"] == "FWD"].sort_values("total_points", ascending=False).head(forward)
                            start_lineup_df = pd.concat([gk, defense_list, midfield_list, attack_list], axis=0).reset_index(drop=True)
                            start_lineup_df = start_lineup_df[["name", "position", "value", "total_points", "team", "total_points"]]
                        
                            # Obtain bench players
                            gk = lineup_df[lineup_df["position"] == "GK"].sort_values("total_points", ascending=False).tail(1)
                            defense_list = lineup_df[lineup_df["position"] == "DEF"].sort_values("total_points", ascending=False).tail(5-defense)
                            midfield_list = lineup_df[lineup_df["position"] == "MID"].sort_values("total_points", ascending=False).tail(5-midfield)
                            attack_list = lineup_df[lineup_df["position"] == "FWD"].sort_values("total_points", ascending=False).tail(3-forward)
                            bench_lineup_df = pd.concat([gk, defense_list, midfield_list, attack_list], axis=0).reset_index(drop=True)
                            bench_lineup_df = bench_lineup_df[["name", "position", "value", "total_points", "team", "total_points"]]

                                    
                            st.write("After game week ", gw, ", the optimal ", defense, "-", midfield, "-", forward, "starting line-up for the team of the season would look like:")
                            plot_formation(start_lineup_df, lineup_df)
                            st.write("And the bench would look like:")
                            plot_bench(bench_lineup_df)
                            #st.dataframe(ordered_lineup_df)
                            #st.write("Total sum of points: ", ordered_lineup_df['total_points'].sum())
                            #st.write("Total budget: ", round(ordered_lineup_df['value'].sum(), 4))
