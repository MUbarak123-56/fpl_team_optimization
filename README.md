# FPL Team Optimization

## Project Overview
This project leverages D-Wave's quantum computing capabilities to solve an optimization problem for selecting the best soccer team formations within given constraints. The goal is to maximize the total points of players in a team without exceeding a total value limit of 1000 and also ensure that the budget doesn't exceed 1000. The formations considered are 4-3-3, 3-5-2, 3-4-3, and 4-4-2, each with specific requirements for the number of goalkeepers, defenders, midfielders, and strikers.

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
git clone https://github.com/your-username/quantum-soccer-optimization.git
cd quantum-soccer-optimization
Install the required Python packages:

## bash
Copy code
pip install -r requirements.txt
This will install D-Wave's Ocean SDK and other necessary libraries.

## Running the Optimization
To run the optimization script for each formation:

Ensure you have set up your D-Wave Leap account and configured your API token.

Execute the script corresponding to the formation you wish to optimize. For example:

## bash
Copy code
python optimize_433.py
Replace optimize_433.py with the appropriate script name for each formation.

## Results
The scripts will output the optimal team composition for each formation, showing the selected players and the total points achieved within the value constraint.

## Contributing
Contributions to improve the optimization model or explore additional formations are welcome. Please feel free to fork the repository, make your changes, and submit a pull request.