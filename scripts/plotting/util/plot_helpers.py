import numpy as np
import matplotlib.pyplot as plt
from db.metrics import Metrics
import re

def alphanum_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def plot_res_scaling(full_data, field, mapping, fun, title_prefix="", ref_data_dict=None, ignore_keys=set()):
    keys = set(ref_data_dict[fun].keys()).difference(ignore_keys)
    resolutions = Metrics.resolutions
    for key in keys:
        data = [full_data[res][mapping][fun][key][field] * 100 for res in resolutions]
        ref = ref_data_dict[fun][key][field]

        plt.figure(figsize=(10, 6))
        plt.plot(Metrics.resolutions_numeric, data, label="data", marker=".")
        plt.plot(Metrics.resolutions_numeric, np.ones((len(data,)))*ref, label="REF", marker=".")
        plt.title("Resolutions of " + mapping + "," + fun + "," + key + "," + field)
        plt.xlabel("Resolution")
        plt.ylabel(field)
        plt.xscale("log")
        plt.yscale("log")
        plt.yticks([0.1, 1, 10, 100], labels=["0.1", "1", "10", "100"])
        plt.xticks(Metrics.resolutions_numeric, labels=[str(n) for n in Metrics.resolutions_numeric])
        plt.legend()
        plt.tight_layout()
        plt.show()

def gather_keys(data_dict, ignore_keys):
    keys = set(data_dict['preCICE']['nn']['sinusoid'].keys())
    for mapper in data_dict.keys():
        for mapping in data_dict[mapper].keys():
            for fun in data_dict[mapper][mapping].keys():
                keys = keys.intersection(data_dict[mapper][mapping][fun].keys())
    keys = keys.difference(ignore_keys)
    return keys

def plot_data_field_merged_bar(data_dict, field, ignore_keys=set(), is_percent=True, savePath=None, useLog=True, override_keys=None, use_ref_scaling=True):
    keys = sorted(gather_keys(data_dict, ignore_keys), key=alphanum_key)
    if override_keys is not None: keys = override_keys
    fun_names = Metrics.fun_names
    mappings = Metrics.mappings
    x_positions = range(len(keys))

    renaming = { "mean_misfit" : "mean misfit",
                 "max_misfit"  : "max misfit",
                 "rms_misfit" : "rms misfit",
                 "glob_cons_tgt" : "global target conservation",
                 "glob_cons_src" : "global source conservation",
                 "l_min" : "l-min",
                 "l_max" : "l-max"
                 }
    mapping_rename = { "nn" : "first order",
                       "np" : "second order",
                       "rbf" : "higher order"}
    opt_percent = ""
    #opt_percent = " (in %)" if is_percent else ""
    FONT_SIZE = 18

    for mapping in mappings:
        for fun_name in fun_names:
            plt.figure(figsize=(10, 6))

            n_groups = len(keys)
            n_items_per_group = len(data_dict.keys())
            x = np.arange(n_groups)
            width = 0.2
            offsets = np.linspace(-width * (n_items_per_group - 1) / 2, width * (n_items_per_group - 1) / 2, n_items_per_group)
            spacing = 0.02
            colors = {'preCICE' : '#A4C8E1', 'ESMF': '#70B8A2', 'YAC' : '#E491A6', 'SCRIP' : '#FFB89E'}
            mapper2idx = {'preCICE': 0, 'ESMF': 1, 'YAC': 2, 'SCRIP': 3}

            for mapper in data_dict.keys():
                field_values = np.array([data_dict[mapper][mapping][fun_name][key][field] for key in keys])
                if use_ref_scaling and mapper != "preCICE" and is_percent: field_values = field_values / 100
                field_values = np.minimum(field_values, 100 * np.ones_like(field_values))

                plt.bar(x + offsets[mapper2idx[mapper]], field_values, width - spacing, color=colors[mapper], label=mapper)

            plt.xticks(ticks=x, labels=list(keys), rotation=45, ha="right", fontsize=FONT_SIZE)  # Rotate if labels are long
            plt.xlabel("Entries", fontsize=FONT_SIZE)
            plt.ylabel(f"{renaming[field]}{opt_percent}", fontsize=FONT_SIZE)
            plt.title(f"{renaming[field]} plot for {fun_name} {mapping_rename[mapping]}", fontsize=FONT_SIZE)
            if useLog: plt.yscale("log")
            # if is_percent: plt.yticks([0.1, 1, 10, 100], labels=["0.1", "1", "10", "100"], fontsize=FONT_SIZE)
            else:
                plt.yticks(fontsize=FONT_SIZE)
            plt.legend(fontsize=FONT_SIZE)
            plt.tight_layout()
            if savePath is not None: plt.savefig(f"{savePath}/{field}_{mapping}_{fun_name}.png")
            plt.show()

def plot_data_field_merged(data_dict, field, ignore_keys=set(), is_percent=True, savePath=None, useLog=True, override_keys=None, use_ref_scaling=True):
    keys = sorted(gather_keys(data_dict, ignore_keys), key=alphanum_key)
    if override_keys is not None: keys = override_keys
    fun_names = Metrics.fun_names
    mappings = Metrics.mappings
    x_positions = range(len(keys))

    renaming = { "mean_misfit" : "mean misfit",
                 "max_misfit"  : "max misfit",
                 "rms_misfit" : "rms misfit",
                 "glob_cons_tgt" : "global target conservation",
                 "glob_cons_src" : "global source conservation",
                 "l_min" : "l-min",
                 "l_max" : "l-max"
                 }
    mapping_rename = { "nn" : "first order",
                       "np" : "second order",
                       "rbf" : "higher order"}
    opt_percent = ""
    #opt_percent = " (in %)" if is_percent else ""
    FONT_SIZE = 18

    for mapping in mappings:
        for fun_name in fun_names:
            plt.figure(figsize=(10, 6))

            for mapper in data_dict.keys():
                field_values = np.array([data_dict[mapper][mapping][fun_name][key][field] for key in keys])
                if use_ref_scaling and mapper != "preCICE" and is_percent: field_values = field_values / 100
                field_values = np.minimum(field_values, 100 * np.ones_like(field_values))

                plt.plot(x_positions, field_values, marker='o', linestyle='-', label=mapper)

            plt.xticks(ticks=x_positions, labels=list(keys), rotation=45, ha="right", fontsize=FONT_SIZE)  # Rotate if labels are long
            plt.xlabel("Entries", fontsize=FONT_SIZE)
            plt.ylabel(f"{renaming[field]}{opt_percent}", fontsize=FONT_SIZE)
            plt.title(f"{renaming[field]} plot for {fun_name} {mapping_rename[mapping]}", fontsize=FONT_SIZE)
            if useLog: plt.yscale("log")
            # if is_percent: plt.yticks([0.1, 1, 10, 100], labels=["0.1", "1", "10", "100"], fontsize=FONT_SIZE)
            else:
                plt.yticks(fontsize=FONT_SIZE)
            plt.legend(fontsize=FONT_SIZE)
            plt.tight_layout()
            if savePath is not None: plt.savefig(f"{savePath}/{field}_{mapping}_{fun_name}.png")
            plt.show()

def plot_data_field(data_dict, field, title_prefix="", ref_data_dict=None, ignore_keys=set(), mapping_name=""):
    fun_names = Metrics.fun_names

    plt.figure(figsize=(10, 6))
    for fun_name in fun_names:
        used_keys = set(data_dict[fun_name].keys())
        if ref_data_dict is not None:
            data_keys = set(data_dict[fun_name].keys())
            ref_keys = set(ref_data_dict[fun_name].keys())
            used_keys = ref_keys.intersection(data_keys)
        used_keys = used_keys.difference(ignore_keys)

        mean_misfits = np.array([data_dict[fun_name][key][field] for key in used_keys])
        mean_misfits = np.minimum(mean_misfits, np.ones_like(mean_misfits))

        x_positions = range(len(used_keys))
        plt.plot(x_positions, mean_misfits * 100, marker='o', linestyle='-', label="preCICE")

        if ref_data_dict is not None:
            mean_misfits = np.array([ref_data_dict[fun_name][key][field] for key in used_keys])
            mean_misfits = np.minimum(mean_misfits, np.ones_like(mean_misfits)*100)
            plt.plot(x_positions, mean_misfits, marker='x', linestyle='-', label=mapping_name)

        plt.xticks(ticks=x_positions, labels=list(used_keys), rotation=45, ha="right")  # Rotate if labels are long
        plt.xlabel("Entries")
        plt.ylabel(field)
        plt.title(f"{title_prefix} {field} Plot for {fun_name}")
        plt.yscale("log")
        plt.yticks([0.1, 1, 10, 100], labels=["0.1", "1", "10", "100"])
        plt.legend()
        plt.tight_layout()
        #plt.savefig("images/" + fun_name + "_" + name)
        plt.show()