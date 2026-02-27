# QDay Prize Submission
[QDay Prize](https://www.qdayprize.org/) Submission

## About

This is an ECDLP Algorithm that uses the Qiskit Framework to define the Quantum Circuit but it executes it on Automatski' Quantum Computers. The code is based off the [Qiskit ECDLP project](https://p51lee.github.io/quantum-computing/qiskit-ecdlp/). It was executed on the 7-bit curve given by the QDay Prize. All curves are listed in the curves.json file and the python code to generate the curves is contained in the curves.py file. AutomatskiKomencoQiskit.py contains the API Bindings to run circuits on Automatski' systems.

## The Author

Aditya has a B.S. in Mechanical Engineering and CFD and an M.S. in Robotics & Image Processing from Indian Institute of Technology, Bombay, India. And has done an executive management program and a financial engineering certificate from Indian Institute of Management, Bangalore, India. He was the R&D Head for Fidelity and an Architect at Thoughtworks a global technology consulting company. He has been involved with Quantum Computing and AI for over 2.5 decades.

He is the CEO and Founder of Automatski a full stack Quantum Computing company which makes Quantum Annealers and Gate Based Quantum Computers.

aditya.yadav@gmail.com

## Intellectual Property

All rights are reserved by Aditya Yadav for Aditya-authored components of this codebase. Rights to third-party or upstream components remain with their respective original authors and licensors.

## Installation

Requires Python v3.11+ to run.
Install dependencies:

```sh
pip install qiskit==1.4.2 qiskit-aer==0.16 
pip install https://p51lee.github.io/assets/python/wheel/qiskit_ecdlp-0.1-py3-none-any.whl
pip install quaspy requests
```

Command to run the code
```sh
python ecdlp_with_qiskit_and_automatski_quantum_computer.py
```

To run the code you will also need the IP Address and Port Number of the Automatski' Quantum Computer. Which is not publiclly available. So if the judges want to run the code they have to get in touch with Aditya who will then share the IP Address and Port Number.
It will need to be entered as follows
```sh
backend = AutomatskiKomencoQiskit(
    host="xxx.xxx.xxx.xxx", 
    port=xxxx
)
```

## The Quantum Computer we used

We used Automatski' Quantum Computer which has the below specs/features
- 170 logical qubits
- 10m gate depth
- 99.999% fidelity
- 'n' milli seconds gate execution time
- 43 minutes coherence

## Running ECDLP for different curves of the competition

### 7 bit curve from the QDay Prize Competition (see curves.json file)

Set these values in the code
```sh
EC_MODULUS = 67
EC_A = 0 #fixed for the QDayPrize
EC_B = 7 #fixed for the QDayPrize
EC_ORDER = 79

NUM_BITS = math.ceil(math.log2(EC_MODULUS))

N_COUNT = 2 * NUM_BITS + 2

point_p = (48, 60)  #Generator POINT
private_key = 56
```

Search for start_guess and set it to 24
```sh
start_guess= 24,
```

so that the minimum ancilla finding routine doesn't spend a long time searching for the correct number of ancilla qubits to be used in building the Quantum Circuit. This is a workaround.

![](https://raw.githubusercontent.com/adityayadav76/qday_prize_submission/refs/heads/main/qdayprize-7bit-curve.png)

### 8 bit curve from the QDay Prize Competition (see curves.json file)

Set these values in the code
```sh
EC_MODULUS = 163
EC_A = 0 #fixed for the QDayPrize
EC_B = 7 #fixed for the QDayPrize
EC_ORDER = 139

NUM_BITS = math.ceil(math.log2(EC_MODULUS))

N_COUNT = 2 * NUM_BITS + 2

point_p = (112, 53)  #Generator POINT
private_key = 103
```

Search for start_guess and set it to 29
```sh
start_guess= 29,
```

so that the minimum ancilla finding routine doesn't spend a long time searching for the correct number of ancilla qubits to be used in building the Quantum Circuit. This is a workaround.

![](https://raw.githubusercontent.com/adityayadav76/qday_prize_submission/refs/heads/main/qdayprize-8bit-curve.png)
