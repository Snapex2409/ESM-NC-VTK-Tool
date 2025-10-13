import json
import numpy as np
import matplotlib.pyplot as plt


def read_json(path):
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except Exception:
        return None

def load_result(path, name='computeMapping', extract=True):
    data = read_json(path)
    if data is None: return None
    data = [d for d in data['traceEvents'] if d['name'].find(name) != -1]
    if not extract: return data

    extracted = [d['dur'] for d in data]
    if len(extracted) == 1: return extracted
    return extracted[1::2]

def load_oasis_result(path, key='   10  cpl_yac_genmap'):
    lines = None
    try:
        with open(path, 'r') as file:
            lines = file.readlines()
    except Exception:
        return 0

    if lines is None: return 0
    lines = [s for s in lines if s.startswith(key)]
    if len(lines) == 0: return 0

    string = lines[-1]
    data = string.split()[2:]
    return float(data[0])

def gather_prc():
    # dur in micro seconds
    base_path = '../../benchmark/strong_scaling/np/nogt_to_icos_masked_by_nogt/vortex'
    ranks = [1, 2, 4, 8]
    iterations = 10
    averages = []
    for pA in [1]:
        for pB in ranks:
            it_results = []
            for i in range(1, iterations + 1):
                path = f"{base_path}/p{pA}_to_p{pB}/it{i}/trace.json"
                it_results.append(load_result(path))
            avg = np.array(it_results).flatten().sum() / (iterations * pB)
            print(f"pA:{pA} pB:{pB} | {avg}")
            averages.append(avg)
    return averages

def gather_oasis():
    # dur in micro seconds
    # yac - rank local map
    print("YAC - rank local map")
    base_path = '../../benchmark/strong_scaling_oasis/RUNDIR_YAC_A/regrid_environment_nogt_icos_bili_vortex_1_'
    ranks = [1, 2, 4, 8]
    iterations = 10
    for n in ranks:
        it_results = []
        for i in range(1, iterations + 1):
            path = f"{base_path}{n}_1_YAC_A/it{i}/model1.timers_0000"
            it_results.append(load_oasis_result(path, '   10  cpl_yac_genmap'))
        avg = np.array(it_results).flatten().sum() / iterations
        print(f"n:{n} | {avg}")

    # yac - global map
    print("YAC - global map")
    base_path = '../../benchmark/strong_scaling_oasis/RUNDIR_YAC_A/regrid_environment_nogt_icos_bili_vortex_1_'
    ranks = [1, 2, 4, 8]
    iterations = 10
    averages = []
    for n in ranks:
        it_results = []
        for i in range(1, iterations + 1):
            path = f"{base_path}{n}_1_YAC_A/it{i}/model1.timers_0000"
            it_results.append(load_oasis_result(path, '    7  cpl_yac_genmap'))
        avg = np.array(it_results).flatten().sum() / iterations
        print(f"n:{n} | {avg}")
        averages.append(avg)
    return averages

def plot_results(prc_results_list, oasis_results_list):
    colors = ['#5684E9', '#E69F00']
    FONT_SIZE = 20
    prc_results_local_A1 = np.array(prc_results_list) #np.array([93703.9, 24251.7, 11414.55, 5169.9125])
    prc_results_local_A1 /= 1e+3 # scale to milliseconds
    oasis_results = np.array(oasis_results_list) #np.array([0.044199999999999996, 0.0273, 0.015860000000000003, 0.009920000000000002])
    oasis_results *= 1e+3 # scale to milliseconds

    # Combine all results into one array
    all_results = np.vstack([prc_results_local_A1, oasis_results])

    # Categories
    categories = ["1", "2", "4", "8"]
    n_groups = len(categories)
    n_bars = all_results.shape[0]
    bar_labels = ["preCICE", "OASIS - YAC"]

    # Plot setup
    fig, ax = plt.subplots(figsize=(10, 6))

    bar_width = 0.45
    x = np.arange(n_groups)

    # Plot each bar group
    for i in range(n_bars):
        ax.bar(x + i * bar_width, all_results[i], bar_width, label=bar_labels[i], color=colors[i])

    # Formatting
    ax.set_xticks(x + bar_width * (n_bars - 1) / 2)
    ax.set_xticklabels(categories, fontsize=FONT_SIZE)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=FONT_SIZE)
    ax.set_ylabel("Time (ms)", fontsize=FONT_SIZE)
    ax.set_xlabel("Ranks", fontsize=FONT_SIZE)
    ax.set_title("Strong Scaling of weight computation timings", fontsize=FONT_SIZE)
    ax.legend(fontsize=FONT_SIZE)
    plt.savefig("../../images/strong_scaling.png")
    plt.show()



if __name__ == '__main__':
    prc = gather_prc()
    oas = gather_oasis()
    plot_results(prc, oas)
