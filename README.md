# FPL Team Optimization
![python](https://img.shields.io/badge/Python-3.9.0%2B-blue)
[![View on Streamlit](https://img.shields.io/badge/Streamlit-View%20on%20Streamlit%20app-ff69b4?logo=streamlit)](https://fpl-team-optimization.streamlit.app/)

#### Authors: Mubarak Ganiyu and Farouk Haroun

## Project Overview
The Fantasy Premier League [[5]](#5) is one of the most competitive fan-based online sporting events in the world. It attracts people from all nations as they compete to see who can rack up the most FPL points through the Premier League season. FPL points are points awarded to Premier League players over the course of the season. When someone signs up to play FPL, they are often prompted to build a squad that comprises of football players in the Premier League. Squad selection comes with certain constraints. You must select exactly 2 goalkeepers, 5 defenders, 5 midfielders and 3 forwards. Your squad budget must not exceed 100 million pounds. No team should have more than 3 players represented in your squad. Given all these information about the FPL and its constraints, we thought it would be great to leverage the power of quantum optimization to assist newcomers with selecting the most optimal squad (i.e. a squad that maximizes its total FPL points per game) while meeting the constraints. Thus, the FPL Team Optimization project commenced. By gaining inspiration from a similar project [[2]](#2) conducted by SPDtek [[4]](#4), we were able to build an optimization algorithm that would assist FPL users with selecting the optimal squad when beginning their FPL journey for the season. 

## Usage 

### Prerequisites
- Python
- D-Wave Ocean SDK
- Pandas (for data manipulation)
- Environment Setup

### Terminal

#### D-Wave's GitHub Codespace

If you are going to run the code on D-Wave's GitHub Codespace, just type in the following command below:

      python squad_selection.py

#### Local Machine

If you are going to run the code on your local machine, make sure to adhere to the following steps:
- Fork this repository
- Use the following command in your local terminal to clone the repo:

      git clone https://github.com/your-github-username/fpl_team_optimization.git
  
- Use the next command to navigate to the folder where the code is stored:
  
      cd fpl_team_optimization
  
- Install all the required packages for making the code functional by running the command below:

      pip install -r requirements.txt
- Open the squad_selection.py file and uncomment the two lines of code below in the file while replacing the [INSERT TOKEN HERE] with your D-Wave API token which can be obtained [here](https://cloud.dwavesys.com/leap/):

        #api_token = [INSERT TOKEN HERE]
        #sampler = LeapHybridSampler(token= api_token)
  
- Use the command below to run the python code for generating an FPL team:
  
      python squad_selection_local.py

**Note:** Upon running either squad_selection.py or squad_selection_local.py, you will be prompted to insert the number of defenders, midfielders and forwards you would like to see in your starting line up for your squad. Make sure all the numbers you input are within the range if not, you will be prompted to re-insert them.

#### Results
After running the code and specifying the number of defenders, midfielders and forwards you want, you will receive an output like the one below:

![Sample Output](images/sample_output.png)

### Web Application

Users can also navigate to the app [here](https://fpl-team-optimization.streamlit.app/) and follow instructions to generate an output that looks like the one below:

![Sample Output App](images/sample_output_app.png)

The app was built via Streamlit, a data science Python package for developing apps suitable for data visualization and other data science related projects.4

## Data

There three datasets being used for this project are obtained in their rawest format from Vaastav's Fantasy Premier League GitHub repo [[1]](#1). The first dataset reflects all the gameweek information for all the players from the first gameweek to the most recent gameweek. The gameweek dataset focuses on metrics such as the position, the game week info and the name of the player. The second dataset reflects all the team information about various players with regards to their form, injuries and chances of playing next round. The third dataset is used to extract information about the players' most recent value. By combining all three datasets and wrangling them, it was possible to build a condensed dataset that focused on important variables such as name, team, total_points, date, position, gameweek, minutes played and FPL points per game. This condensed dataset reflects the top 50 highest rated players (5 goalkeepers, 15 defenders, 15 midfielders and 15 forwards) so far this season in terms of their most recent FPL points per game over season. For a player to be considered for selection, they must be available for the next gameweek (i.e. no injured or suspended or loaned players). Using GitHub Actions, the condensed dataset is updated everyday to reflect Premier League players' most recent performance, so that new users can get the up-to-date optimized FPL team when they use the project's website [here](https://fpl-team-optimization.streamlit.app/) or they can do a git pull for the repo on their local machine prior to running the squad_selection_local.py file. 


## Problem Formulation

The problem was formulated to maximize the total FPL points per game of the squad while meeting various FPL constraints. Below are the objective and constraints in plain english:

**Objective**
- Maximize the FPL points per game

**Constraints**
- The selection of 2 goalkeepers
- The selection of 5 defenders
- The selection of 5 midfielders
- The selection of 3 forwards
- A maximum budget of 100 million pounds
- A team representation of 3 players at maximum.



## References
<a name="1">[1]</a> Vaastav Anand, "Fantasy Premier League," GitHub. Available: https://github.com/vaastav/Fantasy-Premier-League. Accessed: April 13, 2024.

<a name="2">[2]</a> Spdtek, "Line-up Optimization," GitHub. Available: https://github.com/spdtek/Line-up-optimization. Accessed: April 13, 2024.

<a name="3">[3]</a> T. Kumar, S. Singh, and A. Sharma, "Line-up Optimization for Fantasy Sports," arXiv:2112.13668, Dec. 2021. [Online]. Available: https://arxiv.org/ftp/arxiv/papers/2112/2112.13668.pdf. Accessed: April 13, 2024.

<a name="4">[4]</a> SPDTEK, "Home - SPDTEK," SPDTEK. Available: https://www.spdtek.com/home-spdtek. 

<a name="5">[5]</a> Premier League, "Fantasy Premier League," Premier League. Available: https://fantasy.premierleague.com/. Accessed: April 14, 2024.

<a name="6">[6]</a> D-Wave Systems Inc., "D-Wave Documentation Handbook," D-Wave Systems. Available: https://docs.dwavesys.com/docs/latest/doc_handbook.html. Accessed: April 13, 2024.
