# QDay Prize Submission
QDay Prize Submission

## About

This is an ECDLP Algorithm that uses the Qiskit Framework to define the Quantum Circuit but it executes it on Automatski' Quantum Computers. The code is based off the Qiskit ECDLP project.

### Intellectual Property
All rights are reserved by Aditya Yadav for Aditya-authored components of this codebase. Rights to third-party or upstream components remain with their respective original authors and licensors.

## Installation

Requires Python v3.11+ to run.
Install dependencies:

```sh
pip install qiskit==1.4.2 qiskit-aer==0.16 
pip install https://p51lee.github.io/assets/python/wheel/qiskit_ecdlp-0.1-py3-none-any.whl
pip install quaspy 
```

Run the code
```sh
python RSA-Shors-Benchmark-Main.py
```

## Results

### 7 bit curve from the QDay Prize Competition (see curves.json file)
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

![](https://raw.githubusercontent.com/adityayadav76/the-first-quantum-cryptography-benchmarks/refs/heads/main/Runs/RSA/Shors/67297.png)
