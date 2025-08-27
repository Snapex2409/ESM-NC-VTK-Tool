import numpy as np
import matplotlib.pyplot as plt
from scripts.plotting.data_loaders.Metrics import Metrics
import re

def __alphanum_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def __gather_keys(data_dict, ignore_keys):
    keys = set(data_dict['preCICE']['nn']['sinusoid'].keys())
    for mapper in data_dict.keys():
        for mapping in data_dict[mapper].keys():
            for fun in data_dict[mapper][mapping].keys():
                keys = keys.intersection(data_dict[mapper][mapping][fun].keys())
    keys = keys.difference(ignore_keys)
    keys = sorted(keys, key=__alphanum_key)
    return keys

def __gather_funs(data_dict):
    funs = set(data_dict['preCICE']['nn'].keys())
    for mapper in data_dict.keys():
        for mapping in data_dict[mapper].keys():
            funs = funs.intersection(data_dict[mapper][mapping].keys())
    funs = sorted(funs, key=__alphanum_key)
    return funs

def __gather_mappings(data_dict):
    mappings = set(data_dict['preCICE'].keys())
    for mapper in data_dict.keys():
        mappings = mappings.intersection(data_dict[mapper].keys())
    mappings = sorted(mappings, key=__alphanum_key)
    return mappings

def __gather_properties(data_dict, ignore_keys):
    keys     = set(data_dict['preCICE']['nn']['sinusoid'].keys())
    funs     = set(data_dict['preCICE']['nn'].keys())
    mappings = set(data_dict['preCICE'].keys())

    for mapper in data_dict.keys():
        mappings = mappings.intersection(data_dict[mapper].keys())
        for mapping in data_dict[mapper].keys():
            funs = funs.intersection(data_dict[mapper][mapping].keys())
            for fun in data_dict[mapper][mapping].keys():
                keys = keys.intersection(data_dict[mapper][mapping][fun].keys())
    keys = keys.difference(ignore_keys)

    keys     = sorted(keys, key=__alphanum_key)
    funs     = sorted(funs, key=__alphanum_key)
    mappings = sorted(mappings, key=__alphanum_key)
    return keys, funs, mappings

def __generate_constants():
    renaming = {"mean_misfit": "mean misfit",
                "max_misfit": "max misfit",
                "rms_misfit": "rms misfit",
                "glob_cons_tgt": "global target conservation",
                "glob_cons_src": "global source conservation",
                "l_min": "l-min",
                "l_max": "l-max"
                }
    mapping_rename = {"nn": "first order",
                      "np": "second order",
                      "rbf": "higher order"}
    FONT_SIZE = 18
    return renaming, mapping_rename, FONT_SIZE

def __generate_bar_properties(keys, data_dict):
    n_groups = len(keys)
    n_items_per_group = len(data_dict.keys())
    x = np.arange(n_groups)
    width = 0.2
    offsets = np.linspace(-width * (n_items_per_group - 1) / 2, width * (n_items_per_group - 1) / 2,
                          n_items_per_group)
    spacing = 0.02
    colors = {'preCICE': '#A4C8E1', 'ESMF': '#70B8A2', 'YAC': '#E491A6', 'SCRIP': '#FFB89E'}
    mapper2idx = {'preCICE': 0, 'ESMF': 1, 'YAC': 2, 'SCRIP': 3}

    return x, width, offsets, spacing, colors, mapper2idx

def __generate_line_properties(keys, data_dict):
    x_positions = range(len(keys))
    return x_positions

def __plot_fun_bar(field_values, plot_properties, mapper):
    x, width, offsets, spacing, colors, mapper2idx = plot_properties
    plt.bar(x + offsets[mapper2idx[mapper]], field_values, width - spacing, color=colors[mapper], label=mapper)

def __plot_fun_line(field_values, plot_properties, mapper):
    x_positions = plot_properties
    plt.plot(x_positions, field_values, marker='o', linestyle='-', label=mapper)

def __plot_data_field_merged(plot_properties_fun, plot_fun, data_dict, field, ignore_keys=set(), is_percent=True, savePath=None, useLog=True,
                               override_keys=None, use_ref_scaling=True):
    keys, fun_names, mappings = __gather_properties(data_dict, ignore_keys)
    if override_keys is not None: keys = override_keys
    renaming, mapping_rename, FONT_SIZE = __generate_constants()
    plot_properties = plot_properties_fun(keys, data_dict)

    for mapping in mappings:
        for fun_name in fun_names:
            plt.figure(figsize=(10, 6))
            for mapper in data_dict.keys():
                field_values = np.array([data_dict[mapper][mapping][fun_name][key][field] for key in keys])
                if use_ref_scaling and not mapper.startswith("preCICE") and is_percent: field_values = field_values / 100
                field_values = np.minimum(field_values, 100 * np.ones_like(field_values))

                plot_fun(field_values, plot_properties, mapper)

            plt.xticks(ticks=plot_properties[0], labels=list(keys), rotation=45, ha="right", fontsize=FONT_SIZE)  # Rotate if labels are long
            plt.xlabel("Entries", fontsize=FONT_SIZE)
            plt.ylabel(f"{renaming[field]}", fontsize=FONT_SIZE)
            plt.title(f"{renaming[field]} plot for {fun_name} {mapping_rename[mapping]}", fontsize=FONT_SIZE)
            if useLog: plt.yscale("log")
            else: plt.yticks(fontsize=FONT_SIZE)
            plt.legend(fontsize=FONT_SIZE)
            plt.tight_layout()
            if savePath is not None: plt.savefig(f"{savePath}/{field}_{mapping}_{fun_name}.png")
            plt.show()

def plot_data_field_merged_bar(data_dict, field, ignore_keys=set(), is_percent=True, savePath=None, useLog=True, override_keys=None, use_ref_scaling=True):
    __plot_data_field_merged(__generate_bar_properties, __plot_fun_bar, data_dict, field, ignore_keys, is_percent, savePath, useLog, override_keys, use_ref_scaling)

def plot_data_field_merged_line(data_dict, field, ignore_keys=set(), is_percent=True, savePath=None, useLog=True, override_keys=None, use_ref_scaling=True):
    __plot_data_field_merged(__generate_line_properties, __plot_fun_line, data_dict, field, ignore_keys, is_percent, savePath, useLog, override_keys, use_ref_scaling)

def plot_res_scaling(full_data, field, mapping, fun, title_prefix="", ref_data_dict=None, ignore_keys=set()):
    keys = set(ref_data_dict[fun].keys()).difference(ignore_keys)
    resolutions = Metrics.default_resolutions
    for key in keys:
        data = [full_data[res][mapping][fun][key][field] * 100 for res in resolutions]
        ref = ref_data_dict[fun][key][field]

        plt.figure(figsize=(10, 6))
        plt.plot(Metrics.default_resolutions_numeric, data, label="data", marker=".")
        plt.plot(Metrics.default_resolutions_numeric, np.ones((len(data,)))*ref, label="REF", marker=".")
        plt.title("Resolutions of " + mapping + "," + fun + "," + key + "," + field)
        plt.xlabel("Resolution")
        plt.ylabel(field)
        plt.xscale("log")
        plt.yscale("log")
        plt.yticks([0.1, 1, 10, 100], labels=["0.1", "1", "10", "100"])
        plt.xticks(Metrics.default_resolutions_numeric, labels=[str(n) for n in Metrics.default_resolutions_numeric])
        plt.legend()
        plt.tight_layout()
        plt.show()