# FPL Team Optimization
#### Authors: Mubarak Ganiyu and Farouk Haroun

## Project Overview
The Fantasy Premier League [[5]](#5) is one of the most competitive fan-based online sporting events in the world. It attracts people from all nations as they compete to see who can rack up the most FPL points through the Premier League season. FPL points are points awarded to Premier League players over the course of the season. When someone signs up to play FPL, they are often prompted to build a squad that comprises of football players in the Premier League. Squad selection comes with certain constraints. You must select exactly 2 goalkeepers, 5 defenders, 5 midfielders and 3 forwards. Your squad budget must not exceed 100 million pounds. No team should have more than 3 players represented in your squad. Given all these information about the FPL and its constraints, we thought it would be great to leverage the power of quantum optimization to assist newcomers with selecting the most optimal squad while meeting the constraints. Thus, the FPL Team Optimization project commenced. By gaining inspiration from a similar project [[2]](#2) conducted by SPDtek [[4]](#4), we were able to build an optimization algorithm that would assist FPL users with selecting the optimal squad when beginning their FPL journey for the season.

## Data
The optimization uses player data provided in data.xlsx, which includes positions, performance points, and player values. This data is crucial for formulating the optimization problem.


## Usage 

## Prerequisites
Python 3.x
D-Wave Ocean SDK
Pandas (for data manipulation)
Environment Setup
Clone the repository to your local machine:

## bash
Copy code
git clone https://github.com/your-username/fpl_lineup_optimization.git
cd fpl_lineup_optimization
Install the required Python packages:

## bash
Copy code
pip install -r requirements.txt
This will install D-Wave's Ocean SDK and other necessary libraries.

## Running the Optimization
To run the optimization script:

Ensure you have set up your D-Wave Leap account and configured your API token.

If you are running on LEAP directly, run the code below
python formation_selection_no_token.py

If you are running the code locally, run the code below
python formation_selection.py

## Results
The scripts will output the optimal team composition for each formation you inputed, showing the selected players and the total points achieved within the value constraint.

## Model Overview

## References
<a name="1">[1]</a> Vaastav Anand, "Fantasy Premier League," GitHub. Available: https://github.com/vaastav/Fantasy-Premier-League. Accessed: April 13, 2024.

<a name="2">[2]</a> Spdtek, "Line-up Optimization," GitHub. Available: https://github.com/spdtek/Line-up-optimization. Accessed: April 13, 2024.

<a name="3">[3]</a> T. Kumar, S. Singh, and A. Sharma, "Line-up Optimization for Fantasy Sports," arXiv:2112.13668, Dec. 2021. [Online]. Available: https://arxiv.org/ftp/arxiv/papers/2112/2112.13668.pdf. Accessed: April 13, 2024.

<a name="4">[4]</a> SPDTEK, "Home - SPDTEK," SPDTEK. Available: https://www.spdtek.com/home-spdtek. 

<a name="5">[5]</a> Premier League, "Fantasy Premier League," Premier League. Available: https://fantasy.premierleague.com/. Accessed: April 14, 2024.

<a name="6">[6]</a> D-Wave Systems Inc., "D-Wave Documentation Handbook," D-Wave Systems. Available: https://docs.dwavesys.com/docs/latest/doc_handbook.html. Accessed: April 13, 2024.
