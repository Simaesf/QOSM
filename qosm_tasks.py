#!/usr/bin/env python
# coding: utf-8

# 
# ## Task 1 :
# #### The Swap test is a simple quantum circuit which, given two states, allows to compute how much do they differ from each other.
# 
# 1- Provide a variational (also called parametric) circuit which is able to generate the most general 1 qubit state. By most general 1 qubit state we mean that there exists a set of the parameters in the circuit such that any point in the Bloch sphere can be reached. Check that the circuit works correctly by showing that by varying randomly the parameters of your circuit you can reproduce correctly the Bloch sphere.
# Use the circuit built in step 1) and, using the SWAP test, find the best choice of your parameters to reproduce a randomly generated quantum state made with 1 qubit.
# 
# 2- Suppose you are given with a random state, made by N qubits, for which you only know that it is a product state and each of the qubits are in the state | 0 > or | 1>. By product state we mean that it can be written as the product of single qubit states, without the need to do any summation. For example, the state
# |a> = |01>
# Is a product state, while the state
# |b> = |00> + |11>
# Is not.
# 
# 3- Perform a qubit by qubit SWAP test to reconstruct the state. This part of the problem can be solved via a simple grid search.
# 


# ## Solution: 
#########################################################################################################################
#Part 1)


from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute, transpile
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_vector, plot_histogram, plot_state_qsphere, plot_bloch_multivector
from math import pi

import random

get_ipython().run_line_magic('matplotlib', 'inline')


def newqc(theta, phi, lam, qb):
    myqc = QuantumCircuit(1)
    #first we creat a superposition to have equal chances for states |0> and |1>
    myqc.h(0)
    myqc.u(theta, phi, lam, qb)
    return myqc 




theta = random.uniform(0,1)*pi
phi = random.uniform(0,1)*pi
lam = random.uniform(0,1)*pi

print("parameters theta, phi, and lam are: ", theta, phi, lam)

random_circuit = newqc(theta, phi, lam, 0)
state = Statevector.from_instruction(random_circuit)

plot_bloch_multivector (state)
plot_state_qsphere(state, show_state_labels=True)

#############################################################################################################################
# ## Part 2) 


# defining the function to measure the similarity of 2 given quantum circuits using thr swap test

def similarity(circuit1, circuit2, num_qubits):
    overlap_test_qc = QuantumCircuit(3,1)
    overlap_test_qc.h(0)

    overlap_test_qc.compose(circuit1, qubits=[1], inplace=True)
    overlap_test_qc.compose(circuit2, qubits=[2], inplace=True)
    
    for i in range(num_qubits):
        overlap_test_qc.cswap(0,i+1,i+1+num_qubits)
        
    overlap_test_qc.h(0)
    overlap_test_qc.measure([0],[0])
    backend = Aer.get_backend('qasm_simulator')
    job = execute(overlap_test_qc, backend, shots = 10000)
    prob = job.result().get_counts()['0']/10000    
    return prob 


# comparing the random state we generated in part one with an approximated circuit to find the parameters

accuracy = 0
threshold_prob= 0.9
iteration = 0

random_state_qc = QuantumCircuit(1)
random_circuit.initialize(state.data, [0])

while accuracy < threshold_prob:
    t = random.uniform(0,1)*pi
    p = random.uniform(0,1)*pi
    l = random.uniform(0,1)*pi

    approximation_circuit = newqc(t, p, l, 0)
    accuracy = similarity(approximation_circuit, random_state_qc, num_qubits=1)
    iteration += 1

print("The best match was found in ", iteration, "iterations with ",  accuracy*100 , " percent accuracy.")
print("The best choice of parameters for this match is: theta=", t, " phi=", p , " lam= ", l)

state1 = Statevector.from_instruction(approximation_circuit)
plot_bloch_multivector(state1)


###################################################################################################################################

# ## Part 3)


# define a random product state with N qubits: 

N = 3
Allqubits = list(range(2*N+1))
qubits1 = Allqubits[1:N+1]
qubits2 = Allqubits[N+1:2*N+1]

# creating a random state:
def state_label(n): 
    state = "" 
    for i in range(n): 
        bit = str(random.randint(0, 1)) 
        state += bit 
          
    return(state)

qstate = state_label(N) 
print("random quantum state is: ", qstate) 
new_state = Statevector.from_label(qstate)
new_state.data

# create a circuit that represents the product state

state_qcircuit = QuantumCircuit(N)
state_qcircuit.initialize(new_state.data, qubits=list(range(N)))
state_qcircuit.draw('mpl',style={'name': 'bw'},  scale = 1)

# defining a function to creat a N-qubit quantum circuit with a random state given the totation parameters
# on the Bloch sphere

def Nqubit_rand_qc(t,p,l, qubits):
    Nqubit_qc = QuantumCircuit(N)
    for i in range(N):
        t = random.uniform(0,1)*2*pi
        p = random.uniform(0,1)*2*pi
        l = random.uniform(0,1)*2*pi
        Nqubit_qc.u(t, p, l, i)
    Nqubit_qc.draw('mpl',style={'name': 'bw'},  scale = 1.2)
    return(Nqubit_qc)

# creat a N-qubit circuit for random state on Bloch sphere:

Nqubit_qc = Nqubit_rand_qc(t,p,l, qubits2)
Nqubit_qc.draw()

# defining the function to measure the similarity of 2 given quantum circuits using the swap test

def similarity2(circuit1, circuit2, num_qubits):
    overlap_test_qc = QuantumCircuit(2*N+1,1)
    overlap_test_qc.h(0)
    
    overlap_test_qc.compose(circuit1, qubits=qubits1, inplace=True)
    overlap_test_qc.compose(circuit2, qubits=qubits2, inplace=True)
    
    for i in range(num_qubits):
        overlap_test_qc.cswap(0,i+1,i+1+num_qubits)
        
    overlap_test_qc.h(0)
    overlap_test_qc.measure([0],[0])
    backend = Aer.get_backend('qasm_simulator')
    job = execute(overlap_test_qc, backend, shots = 10000)
    prob = job.result().get_counts()['0']/10000    
    return prob 

# comparing the random state we generated in part one with an approximated circuit to find the parameters

accuracy = 0
threshold_prob= 0.9
iteration = 0

while accuracy < threshold_prob:
    Nqubit_qc = QuantumCircuit(N)
    for i in range(N):
        t = random.uniform(0,1)*2*pi
        p = random.uniform(0,1)*2*pi
        l = random.uniform(0,1)*2*pi
        Nqubit_qc.u(t, p, l, i)
    accuracy = similarity2(state_qcircuit, Nqubit_qc, num_qubits=N)
    iteration += 1
print("The best match was found in ", iteration, "iterations with ",  accuracy*100 , " percent accuracy.")
print("The best choice of parameters for this match is: theta=", t, " phi=", p , " lam= ", l)
state2 = Statevector.from_instruction(Nqubit_qc)
plot_state_qsphere(state2)
