# FPL Team Optimization

## Project Overview
The FPL Team Optimization project leverages .

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

## References
<a name="1">[1]</a> Vaastav Anand, "Fantasy Premier League," GitHub. Available: https://github.com/vaastav/Fantasy-Premier-League. Accessed: April 13, 2024.

<a name="2">[2]</a> D-Wave Systems Inc., "D-Wave Documentation Handbook," D-Wave Systems. Available: https://docs.dwavesys.com/docs/latest/doc_handbook.html. Accessed: April 13, 2024.

<a name="3">[3]</a> Spdtek, "Line-up Optimization," GitHub. Available: https://github.com/spdtek/Line-up-optimization. Accessed: April 13, 2024.

<a name="4">[4]</a> T. Kumar, S. Singh, and A. Sharma, "Line-up Optimization for Fantasy Sports," arXiv:2112.13668, Dec. 2021. [Online]. Available: https://arxiv.org/ftp/arxiv/papers/2112/2112.13668.pdf. Accessed: April 13, 2024.

<a name="5">[5]</a> SPDTEK, "Home - SPDTEK," SPDTEK. Available: https://www.spdtek.com/home-spdtek. 
