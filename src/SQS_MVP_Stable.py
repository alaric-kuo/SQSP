import numpy as np
import matplotlib.pyplot as plt
import warnings
from scipy.sparse import SparseEfficiencyWarning
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.circuit.library import PauliEvolutionGate
from qiskit import QuantumCircuit

# --- [1] 環境優化：消除 Scipy 稀疏矩陣轉換警告 ---
warnings.filterwarnings("ignore", category=SparseEfficiencyWarning)

def run_sqsp_simulation(is_damaged=False):
    """
    執行 SQSP (Semantic Quantum Structural Protocol) 模擬
    is_damaged: 模擬結構中層是否發生剛度異變
    """
    num_floors = 4
    times = np.linspace(0, 10, 80)
    
    # 定義結構哈密頓量 (Hamiltonian Simulation)
    # 正常剛度 k=1.0, 異變剛度 k=0.1
    ops = []
    for i in range(num_floors - 1):
        # 模擬二樓與三樓間的能量傳遞路徑異變
        k = 0.1 if (is_damaged and i == 1) else 1.0
        ops.append(("XX", [i, i+1], k))
        ops.append(("YY", [i, i+1], k))

    H = SparsePauliOp.from_sparse_list(ops, num_qubits=num_floors)
    
    # 初始狀態：地震動能由地基 (Floor 0) 注入
    init_state = Statevector.from_label('0001') 
    
    # 追蹤每一層樓的能量分布 (機率幅演化)
    energy_history = {f'Floor {i}': [] for i in range(num_floors)}

    for t in times:
        evo_gate = PauliEvolutionGate(H, time=t)
        qc = QuantumCircuit(num_floors)
        qc.append(evo_gate, range(num_floors))
        
        probs = init_state.evolve(qc).probabilities()
        for i in range(num_floors):
            energy_history[f'Floor {i}'].append(probs[2**i])

    return times, energy_history

# --- [2] 執行 SQSP 數據收集 ---
t, data_nominal = run_sqsp_simulation(is_damaged=False)
_, data_impedance = run_sqsp_simulation(is_damaged=True)

# --- [3] 語意邏輯診斷引擎 (SQSP Semantic Engine) ---
def get_semantic_report(name, history):
    """
    將數值演化轉譯為診斷語意，並顯化關鍵能流數據 (0.97 / 0.65)
    """
    peak_roof = max(history['Floor 3'])
    
    # 語意標籤映射：Nominal(穩健) / Impedance(受阻) / Critical(失效)
    if peak_roof > 0.8:
        status = "【Nominal 額定/穩健】"
        desc = "能流貫通，結構各層有效分擔能量，完整性與守護韌性極高。"
    elif peak_roof > 0.4:
        status = "【Impedance 阻抗/受阻】"
        desc = "能量傳遞路徑出現淤滯，提示中層剛度發生變異，建議專家介入關注。"
    else:
        status = "【Critical 臨界/失效】"
        desc = "頂端能量感知極低，結構生命線發生斷裂，需立即執行搶修決策。"
    
    # 在回報中顯化具體數值，對標「紅外線眼鏡」的診斷邏輯
    return f"{name} >> 狀態：{status} (能流效率: {peak_roof:.2f}) | 描述：{desc}"

# --- [4] 視覺化繪圖：量子紅外線眼鏡視覺輸出 ---
plt.style.use('seaborn-v0_8-muted')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# 繪製穩健結構 (Case A)
for floor, trace in data_nominal.items():
    ax1.plot(t, trace, label=floor, linewidth=2)
ax1.set_title("SQSP Case A: Nominal Structure (Full Energy Connection)", fontsize=14)
ax1.set_ylabel("Energy Distribution")
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.3)

# 繪製受阻結構 (Case B)
for floor, trace in data_impedance.items():
    ax2.plot(t, trace, label=floor, linewidth=2)
ax2.set_title("SQSP Case B: Impedance at Mid-Level (Energy Reflex)", fontsize=14)
ax2.set_ylabel("Energy Distribution")
ax2.set_xlabel("Time (s)")
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- [5] 輸出 SQSP 診斷報告 (顯化 0.97 與 0.65) ---
print("="*85)
print("  Semantic Quantum Structural Protocol (SQSP) 診斷報告  ")
print("="*85)
print(get_semantic_report("健康監測模組", data_nominal))
print(get_semantic_report("異變監測模組", data_impedance))
print("="*85)
print("註：本報告作為專家既有裝備之輔助增強。數值反映了結構在量子全像模擬下的生機能量傳遞率。")