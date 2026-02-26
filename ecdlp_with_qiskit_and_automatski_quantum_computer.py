"""
Static ECDLP with Qiskit (No dynamic circuits)
Python 3.11
pip install qiskit==1.4.2 qiskit-aer==0.16 
pip install https://p51lee.github.io/assets/python/wheel/qiskit_ecdlp-0.1-py3-none-any.whl
pip install quaspy requests
"""

import math
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFT

# ============================================================
# Elliptic Curve Parameters
# ============================================================


#
# QDayPrize 7 bit curve

EC_MODULUS = 67
EC_A = 0 #fixed for the QDayPrize
EC_B = 7 #fixed for the QDayPrize
EC_ORDER = 79

NUM_BITS = math.ceil(math.log2(EC_MODULUS))

N_COUNT = 2 * NUM_BITS + 2

point_p = (48, 60)  #Generator POINT
private_key = 56


# ============================================================
# Classical Elliptic Curve Arithmetic
# ============================================================

def classical_point_self_addition(point):
    x, y = point
    if x is None and y is None:
        return None, None

    slope = ((3 * x**2 + EC_A) * pow(2 * y, -1, EC_MODULUS)) % EC_MODULUS
    xr = (slope**2 - 2 * x) % EC_MODULUS
    yr = (slope * (x - xr) - y) % EC_MODULUS
    return xr, yr


def classical_point_addition(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    if x2 is None and y2 is None:
        return point1
    if x1 is None and y1 is None:
        return point2

    if x1 == x2 and y1 == y2:
        return classical_point_self_addition(point1)
    elif x1 == x2:
        return None, None

    slope = ((y2 - y1) * pow((x2 - x1), -1, EC_MODULUS)) % EC_MODULUS
    xr = (slope**2 - x1 - x2) % EC_MODULUS
    yr = (slope * (x1 - xr) - y1) % EC_MODULUS
    return xr, yr


def classical_point_doubling(point, multiplier):
    res = (None, None)
    acc = point

    while multiplier > 0:
        if multiplier & 1:
            res = classical_point_addition(res, acc)
        acc = classical_point_self_addition(acc)
        multiplier >>= 1

    return res


point_q = classical_point_doubling(point_p, private_key)


# ============================================================
# Generate Required EC Points
# ============================================================

points = []

# [P, 2P, 4P, ...]
for i in range(NUM_BITS + 1):
    points.append(classical_point_doubling(point_p, 2**i))

# [Q, 2Q, 4Q, ...]
for i in range(NUM_BITS + 1):
    points.append(classical_point_doubling(point_q, 2**i))
    
#
# Ancilla calculator
#
from qiskit import QuantumCircuit, QuantumRegister
from qiskit_ecdlp.api.CircuitChooser import CircuitChooser
from qiskit_ecdlp.api.CircuitNotSupportedError import CircuitNotSupportedError


def find_minimum_ancilla(NUM_BITS, points, EC_MODULUS, start_guess=1, max_search=500):
    """
    Tries increasing clean ancilla until qiskit_ecdlp point adder builds successfully.
    Returns the minimum clean ancilla required.
    """

    print("Searching for minimum clean ancilla...")

    for anc_count in range(start_guess, max_search + 1):
        print(anc_count)
        try:
            # Dummy registers just to test circuit construction
            qreg_count = QuantumRegister(N_COUNT, "count")
            qreg_psi = QuantumRegister(2 * NUM_BITS, "psi")
            qreg_anc = QuantumRegister(anc_count, "anc")
            creg = ClassicalRegister(N_COUNT, "cl")
            test_circuit = QuantumCircuit(qreg_count, qreg_psi, qreg_anc, creg)

            # Try building ONE point addition (worst-case cost)
            point_addition_circuit = (
                CircuitChooser()
                .choose_component(
                    "QCECPointAdderIP",
                    (NUM_BITS, points[0], EC_MODULUS, 1, True),
                    dirty_available=0,
                    clean_available=anc_count,
                )
                .get_circuit()
            )

            # If we reached here — it works
            print(f"✔ Minimum clean ancilla found: {anc_count}")
            return anc_count

        except (CircuitNotSupportedError, IndexError, Exception):
            # Not enough ancilla — try again
            continue

    raise RuntimeError("Failed to find sufficient ancilla within max_search limit.")

# ============================================================
# Quantum Registers
# ============================================================

min_ancilla = find_minimum_ancilla(
    NUM_BITS,
    points,
    EC_MODULUS,
    start_guess= 24, #2 * NUM_BITS + 4,  
    max_search=300
)

# Add small safety margin
ANCILLA_COUNT = min_ancilla #+ 2

print("Using ancilla:", ANCILLA_COUNT)
print(f'Num Of Bits {NUM_BITS}')
print(f"Base Point (P): {point_p}")
print(f"Public Key (Q = {private_key}P): {point_q}")
#import sys
#sys.exit()

qreg_count = QuantumRegister(N_COUNT, "count")
qreg_psi = QuantumRegister(2 * NUM_BITS, "psi")
#qreg_anc = QuantumRegister(2 * NUM_BITS + 4, "anc")
#qreg_anc = QuantumRegister(8 * NUM_BITS + 20, "anc")
qreg_anc = QuantumRegister(ANCILLA_COUNT, "anc")
creg = ClassicalRegister(N_COUNT, "cl")

circuit = QuantumCircuit(qreg_count, qreg_psi, qreg_anc, creg)




# ============================================================
# Step 1: Superposition on Counting Register
# ============================================================

for i in range(N_COUNT):
    circuit.h(qreg_count[i])


# ============================================================
# Step 2: Controlled Elliptic Curve Additions
# ============================================================

from qiskit_ecdlp.api.CircuitChooser import CircuitChooser

for k in range(N_COUNT):

    point_addition_circuit = (
        CircuitChooser()
        .choose_component(
            "QCECPointAdderIP",
            (NUM_BITS, points[k], EC_MODULUS, 1, True),
            dirty_available=0,
            clean_available=len(qreg_anc),
        )
        .get_circuit()
    )

    circuit.append(
        point_addition_circuit,
        [qreg_count[k]] + list(qreg_psi) + list(qreg_anc),
    )


# ============================================================
# Step 3: Apply Full Inverse QFT
# ============================================================

iqft = QFT(N_COUNT, inverse=True, do_swaps=False)
circuit.append(iqft, qreg_count)


# ============================================================
# Step 4: Final Measurement
# ============================================================

circuit.measure(qreg_count, creg)


# ============================================================
# Run on Automatski Backend
# ============================================================

import sys
sys.path.append('../../python/')
from AutomatskiKomencoQiskit import AutomatskiKomencoQiskit

NUM_SHOTS = 100000

backend = AutomatskiKomencoQiskit(
    host="xxx.xxx.xxx.xxx", 
    port=80
)

circuit = transpile(
    circuit,
    basis_gates=[
        'ccx','ccz','cp','crz','cs','csdg','cswap','cu',
        'cx','cy','cz','h','id','measure','p','rx','ry','rz',
        's','sdg','swap','sx','sxdg','t','tdg','u','x','y','z'
    ],
    optimization_level=3
)

result_sim = backend.run(circuit, repetitions=NUM_SHOTS, topK=100)
counts = result_sim.get_counts(None)

#print("Results:", counts)


# ============================================================
# Classical Post-Processing
# ============================================================

from quaspy.math.groups import (
    PointOnShortWeierstrassCurveOverPrimeField,
    ShortWeierstrassCurveOverPrimeField,
)
from quaspy.logarithmfinding.general.postprocessing import (
    solve_j_k_for_d_given_r
)

result_list = []

for key, value in counts.items():
    j = int(key[: N_COUNT // 2], 2)
    k = int(key[N_COUNT // 2:], 2)
    result_list.append((j, k, value))

num_correct = 0
num_wrong = 0
m = -1

quaspy_curve = ShortWeierstrassCurveOverPrimeField(
    EC_A, EC_B, EC_MODULUS
)

for j, k, freq in result_list:

    m_cand = solve_j_k_for_d_given_r(
        j,
        k,
        NUM_BITS + 1,
        0,
        NUM_BITS + 1,
        PointOnShortWeierstrassCurveOverPrimeField(
            point_p[0], point_p[1], E=quaspy_curve
        ),
        PointOnShortWeierstrassCurveOverPrimeField(
            point_q[0], point_q[1], E=quaspy_curve
        ),
        EC_ORDER,
    )

    if m_cand is not None and \
        classical_point_doubling(point_p, m_cand) == point_q:

        if m != -1:
            m = min(m, int(m_cand))
        else:
            m = int(m_cand)

        num_correct += freq
    else:
        num_wrong += freq

m_correct = classical_point_doubling(point_p, m) == point_q

print(f"Correct: {num_correct}, Wrong: {num_wrong}")
print(f"Private key: {private_key}, Found key: {m}, Correct: {m_correct}")