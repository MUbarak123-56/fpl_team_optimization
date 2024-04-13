# FPL Team Optimization

## Project Overview
This project leverages D-Wave's quantum computing capabilities to solve an optimization problem for selecting the best soccer team formations within given constraints. The goal is to maximize the total points of players in a team without exceeding a total budget doesn't exceed 70 FPL currency. The formations considered are 4-3-3, 3-5-2, 3-4-3, and 4-4-2, each with specific requirements for the number of goalkeepers, defenders, midfielders, and strikers.

## Data
The optimization uses player data provided in data.xlsx, which includes positions, performance points, and player values. This data is crucial for formulating the optimization problem.

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

## Inspiration

## References
