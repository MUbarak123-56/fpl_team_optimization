import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

data = pd.read_csv("https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2023-24/gws/merged_gw.csv")

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

latest_df = new_df[new_df["date"]==max(new_df["date"])][["name", "team", "total_points", "date", "position", "value", "GW"]].reset_index(drop=True)

gk = latest_df[latest_df["position"]=="GK"].sort_values("total_points", ascending=False).reset_index(drop=True).head(5)
defenders = latest_df[latest_df["position"]=="DEF"].sort_values("total_points", ascending=False).reset_index(drop=True).head(10)
midfielders = latest_df[latest_df["position"]=="MID"].sort_values("total_points", ascending=False).reset_index(drop=True).head(10)
forwards = latest_df[latest_df["position"]=="FWD"].sort_values("total_points", ascending=False).reset_index(drop=True).head(10)

total_df = pd.concat([gk, defenders, midfielders, forwards], axis = 0).sort_values("position", ascending=False).reset_index(drop=True)
total_df.to_excel("data.xlsx", index=False)
