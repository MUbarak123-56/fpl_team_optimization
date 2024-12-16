import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

data = pd.read_csv("https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2024-25/gws/merged_gw.csv", on_bad_lines='skip')

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

cumulative_df = accumulated(data)

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

latest_df = new_df[new_df["date"]==max(new_df["date"])][["name", "team", "total_points", "date", "position", "value", "GW", "minutes"]].reset_index(drop=True)
df2 = pd.read_csv("https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2023-24/players_raw.csv")
df2["name"] = df2["first_name"] + " " + df2["second_name"]
df2 = df2[["name", "news_added", "news", "points_per_game", "team", "form",'chance_of_playing_next_round',
       'chance_of_playing_this_round']]
df3 = pd.read_csv("https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2023-24/teams.csv")
df_new = df2.merge(df3, left_on = "team", right_on="id")
df_new = df_new.rename(columns={"name_x":"name", "team":"team_code","name_y":"team", "form_x":"form"})
df_new=df_new[["name", "team", "news", "news_added", "points_per_game", "form",'chance_of_playing_next_round',
       'chance_of_playing_this_round']]
tot_df = df_new.merge(latest_df, on=["name","team"])
tot_df["id"] = tot_df.index + 1

df_value = pd.read_csv("https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2023-24/cleaned_players.csv")
df_value["name"] = df_value["first_name"] + " " + df_value["second_name"]
df_value["id"] = df_value.index + 1
df_value = df_value[["id", "name", "now_cost"]]

tot_df = tot_df.merge(df_value, on = "id")

tot_df = tot_df[tot_df["news"].isna()].reset_index(drop=True)
#tot_df = tot_df[~tot_df["chance_of_playing_this_round"].isin(["0", "None"])].reset_index(drop=True)

tot_df = tot_df[(tot_df["points_per_game"] > 0)].reset_index(drop=True)
tot_df = tot_df.drop(["value", "name_y"], axis = 1)
tot_df = tot_df.rename(columns={"now_cost":"value", "name_x":"name"})
tot_df = tot_df[["name", "team", "total_points", "date", "position", "value", "GW", "minutes", "points_per_game"]]

tot_df = tot_df[tot_df["minutes"]>=0.3*max(tot_df["minutes"])].reset_index(drop=True)

tot_df.to_excel("total_data.xlsx", index=False)



gk = tot_df[tot_df["position"]=="GK"].sort_values("points_per_game", ascending=False).reset_index(drop=True).head(5)
defenders = tot_df[tot_df["position"]=="DEF"].sort_values("points_per_game", ascending=False).reset_index(drop=True).head(15)
midfielders = tot_df[tot_df["position"]=="MID"].sort_values("points_per_game", ascending=False).reset_index(drop=True).head(15)
forwards = tot_df[tot_df["position"]=="FWD"].sort_values("points_per_game", ascending=False).reset_index(drop=True).head(15)

use_df = pd.concat([gk, defenders, midfielders, forwards], axis = 0).sort_values("position", ascending=False).reset_index(drop=True)

use_df.to_excel("use_data.xlsx", index=False)
