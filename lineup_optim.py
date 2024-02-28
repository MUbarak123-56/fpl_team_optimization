# Copyright 2021 Promoción y Desarrollo de Sistemas Automáticos SLU
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# ------ Import necessary packages ----

import pandas as pd

from pyqubo import Constraint, Array
import neal
from dwave.system import DWaveSampler, EmbeddingComposite


# Read players rating from CSV
column_names = ["Variable", "Player", "Position", "Rating"]
players_df = pd.read_csv("players.csv", names=column_names)
ratings = players_df['Rating'].tolist()

# Ask user for formation to optimize
n = ['1', '2']
choice = input('Choose formation ([1] for 4-3-3 (default) or 2 for 4-3-2-1): ')
if choice not in n:
    choice = 1
choice = int(choice)


# Initialize problem parameters
M = 90.5    # Constraints coefficient
N = 43      # Number of variables
nS = 10     # Number of slack variables

# Create arrays of BINARY variables
x = Array.create('x', shape=N, vartype='BINARY')
a = Array.create('a', shape=nS, vartype='BINARY')

# Hamiltonian for the objective function
HZ = sum(n * x for x, n in zip(x, ratings))

# General constraints

C1 = M * Constraint((sum(x[n] for n in range(0, 43)) - 11)**2,
                    label='11 players team')
C2 = M * Constraint((sum(x[n] for n in range(0, 2)) - 1)**2,
                    label='1 goal keeper')
C3 = M * Constraint((sum(x[n] for n in range(2, 7)) - 2)**2,
                    label='x2+x3+x4+x5+x6=2')
C4 = M * Constraint((x[7] - 1)**2,
                    label='x7=1')
C5 = M * Constraint((sum(x[n] for n in range(8, 11)) - 1)**2,
                    label='x8+x9+x10=1')
C6 = M * Constraint((sum(x[n] for n in range(38, 43)) - 1)**2,
                    label='x38+x39+x40+x41+x42=1')

# Constraints specific of formation 4-3-3


C7 = M * Constraint((sum(x[n] for n in range(16, 28)) - 3)**2,
                    label='x16+x17+x18+x19+x20+x21+x22+x23+x24+x25+x26+x27+=3')
C8 = M * Constraint((sum(x[n] for n in range(33, 36)) - 1)**2,
                    label='x33+x34+x35=1')
C9 = M * Constraint((sum(x[n] for n in range(36, 38)) - 1)**2,
                    label='x36+x37=1')

# Constraints specific of formation 4-2-3-1

C10 = M * Constraint((sum(x[n] for n in range(11, 16)) - 2)**2,
                     label='x11+x12+x13+x14+x15=2')
C11 = M * Constraint((sum(x[n] for n in range(28, 33)) - 3)**2,
                     label='x28+x29+x30+x31+x32=3')

# Inequalities to avoid line-up solutions with the same player more than once

I1 = M * Constraint((x[7] + x[11] + x[16] + a[0] - 1)**2,
                    label='x7+x11+x16<=1')
I2 = M * Constraint((x[8] + x[12] + a[1] - 1)**2,
                    label='x8+x12<=1')
I3 = M * Constraint((x[9] + x[13] + x[17] + a[2] - 1)**2,
                    label='x9+x13+x17<=1')
I4 = M * Constraint((x[14] + x[19] + x[28] + a[3] - 1)**2,
                    label='x14+x19+x28<=1')
I5 = M * Constraint((x[10] + x[21] + a[4] - 1)**2,
                    label='x10+x21<=1')
I6 = M * Constraint((x[15] + x[23] + a[5] - 1)**2,
                    label='x15+x23<=1')
I7 = M * Constraint((x[25] + x[29] + a[6] - 1)**2,
                    label='x25+x29<=1')
I8 = M * Constraint((x[31] + x[33] + a[7] - 1)**2,
                    label='x31+x33<=1')
I9 = M * Constraint((x[36] + x[39] + a[8] - 1)**2,
                    label='x36+x39<=1')
I10 = M * Constraint((x[27] + x[32] + x[34] + x[37] + x[41] + a[9] - 1)**2,
                     label='x27+x32+x34+x37+x41<=1')

if choice == 1:
    # Hamiltonian for formation 4-3-3
    H = -1 * HZ + C1 + C2 + C3 + C4 + C5 + C6 + C7 + C8 + \
        C9 + I1 + I2 + I3 + I4 + I5 + I6 + I7 + I8 + I9 + I10
else:
    # Hamiltonian for formation 4-3-2-1
    H = -1 * HZ + C1 + C2 + C3 + C4 + C5 + C6 + C10 + C11 + \
        I1 + I2 + I3 + I4 + I5 + I6 + I7 + I8 + I9 + I10


# Compile model and create a BQM

model = H.compile()
qubo, offset = model.to_qubo()
bqm = model.to_bqm()

# Uncomment to solve problem by simulation
# sa = neal.SimulatedAnnealingSampler()
# sampleset = sa.sample(bqm, num_reads=10000)

# Solve problem with QPU
api_token = 'DEV-257ed80ce0a221025ddaa4b7acb440d9978e1f42'
sampler = LeapHybridSampler(token= api_token)
sampleset = sampler.sample(bqm,
                            label="SPDtek - Soccer line-up optimization")


# Decode samples and select the best one
decoded_samples = model.decode_sampleset(sampleset)
best_sample = min(decoded_samples, key=lambda x: x.energy)

# Print to see if constraints are fulfilled
print(best_sample.constraints())


# Print results for best line-up
lineup_df = pd.DataFrame(best_sample.sample.items())
lineup_df.columns = ['Variable', 'Selected']
lineup_df = lineup_df[(lineup_df['Variable'].str.startswith(
    'x', na=False)) & (lineup_df['Selected'] == 1)]
lineup_df = players_df.merge(lineup_df, on=['Variable'])

# Print line-up and maximized energy for the objective function
print(lineup_df)
print(lineup_df['Rating'].sum())
