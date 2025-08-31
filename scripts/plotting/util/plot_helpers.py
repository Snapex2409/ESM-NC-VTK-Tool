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
                               override_keys=None, use_ref_scaling=True, yrange=None):
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
            if yrange is not None:
                ylimits, yticks = yrange
                plt.ylim(ylimits)
                plt.yticks(fontsize=FONT_SIZE, ticks=yticks)
            plt.tight_layout()
            if savePath is not None: plt.savefig(f"{savePath}/{field}_{mapping}_{fun_name}.png")
            plt.show()

def plot_data_field_merged_bar(data_dict, field, ignore_keys=set(), is_percent=True, savePath=None, useLog=True, override_keys=None, use_ref_scaling=True, yrange=None):
    __plot_data_field_merged(__generate_bar_properties, __plot_fun_bar, data_dict, field, ignore_keys, is_percent, savePath, useLog, override_keys, use_ref_scaling, yrange)

def plot_data_field_merged_line(data_dict, field, ignore_keys=set(), is_percent=True, savePath=None, useLog=True, override_keys=None, use_ref_scaling=True, yrange=None):
    __plot_data_field_merged(__generate_line_properties, __plot_fun_line, data_dict, field, ignore_keys, is_percent, savePath, useLog, override_keys, use_ref_scaling, yrange)

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

def create_overlapped_bar_plots(data_dict, field, override_keys, save_path, is_percent=True, use_ref_scaling=True, yrange=None):
    keys, fun_names, mappings = __gather_properties(data_dict, set())
    if override_keys is not None: keys = override_keys
    plt_data = np.zeros((len(keys), 3, 4))
    order2idx = {'nn': 0, 'np': 1, 'rbf': 2}
    mapper2idx = {'preCICE': 0, 'ESMF': 1, 'YAC': 2, 'SCRIP': 3}
    orders = ['nn', 'np', 'rbf']
    mappers = ['preCICE', 'ESMF', 'YAC', 'SCRIP']
    colors = [
        # mapper preCICE - order nn, np, rbf
        ['#A4C8E1', '#80A5C3', '#386890'],
        # mapper ESMF - order nn, np, rbf
        ['#70B8A2', '#40826D', '#255447'],
        # mapper YAC - order nn, np, rbf
        ['#F3CDD6', '#E491A6', '#96384F'],
        # mapper SCRIP - order nn, np, rbf
        ['#FFB89E', '#FF8559', '#965F4B']
    ]
    renaming, _, _ = __generate_constants()
    n_categories = len(keys)
    n_samples = 4
    x = np.arange(n_categories)
    width = 0.2  # Width of each sample group
    offsets = np.linspace(-width * (n_samples - 1) / 2,
                          width * (n_samples - 1) / 2,
                          n_samples)
    spacing = 0.01

    def plt_fig(data, fun, current_orders, name=""):
        fig, ax = plt.subplots(figsize=(10, 4))
        for mapper in mappers:
            for order in current_orders:  # layer
                values = data[:, order2idx[order], mapper2idx[mapper]]
                wfac = 1.0
                if order == 'rbf': wfac = 2.0
                ax.bar(x + offsets[mapper2idx[mapper]], values, width / wfac - spacing,
                       color=colors[mapper2idx[mapper]][order2idx[order]], label=f'{mapper} {order}')

        ax.set_xticks(x)
        ax.set_xticklabels(keys, rotation=45)
        ax.set_ylabel(renaming[field])
        ax.set_title(f'{fun}')
        ax.set_yscale('log')
        if yrange is None: ax.set_ylim([np.min(data), np.max(data)])
        else:
            ylimits, yticks = yrange
            ax.set_ylim(ylimits)
            ax.set_yticks(yticks)

        plt.tight_layout()
        if name != "": plt.savefig(f'{save_path}/{name}.png')
        plt.show()

    for fun in fun_names:
        for order in orders:
            for mapper in mappers:
                factor = 1.
                if use_ref_scaling and not mapper.startswith("preCICE") and is_percent: factor = 100.
                plt_data[:, order2idx[order], mapper2idx[mapper]] = np.array([data_dict[mapper][order][fun][key][field] for key in keys]) / factor

        plt_fig(plt_data, fun, ['nn'], f"overlap-{field}-{fun}0")
        plt_fig(plt_data, fun, ['nn', 'np'], f"overlap-{field}-{fun}1")
        plt_fig(plt_data, fun, ['nn', 'np', 'rbf'], f"overlap-{field}-{fun}2")

def create_overview_plot(data_merged, pairs, fun, save_path, yrange_mean_misfit=None, yrange_glob_cons_src=None):
    x = np.arange(len(pairs))
    fig, axs = plt.subplots(4, 2, figsize=(10, 12))
    # preCICE
    axs[0, 0].plot(x, [data_merged['preCICE']['nn'][fun][key]['mean_misfit'] for key in pairs], color='red', label='first order', marker='.')
    axs[0, 0].plot(x, [data_merged['preCICE']['np'][fun][key]['mean_misfit'] for key in pairs], color='green', label='second order', marker='x')
    axs[0, 0].plot(x, [data_merged['preCICE']['rbf'][fun][key]['mean_misfit'] for key in pairs], color='blue', label='higher order', marker='D')
    # axs[0, 0].set_title('preCICE mean misfit')
    axs[0, 0].text(0.01, 0.99, "preCICE", transform=axs[0, 0].transAxes, fontsize=14, va='top', ha='left')
    axs[0, 1].plot(x, [data_merged['preCICE']['nn'][fun][key]['glob_cons_src'] for key in pairs], color='red', label='first order', marker='.')
    axs[0, 1].plot(x, [data_merged['preCICE']['np'][fun][key]['glob_cons_src'] for key in pairs], color='green', label='second order', marker='x')
    axs[0, 1].plot(x, [data_merged['preCICE']['rbf'][fun][key]['glob_cons_src'] for key in pairs], color='blue', label='higher order', marker='D')
    # axs[0, 1].set_title('preCICE global source conservation')
    axs[0, 1].text(0.01, 0.99, "preCICE", transform=axs[0, 1].transAxes, fontsize=14, va='top', ha='left')
    # ESMF
    axs[1, 0].plot(x, [data_merged['ESMF']['nn'][fun][key]['mean_misfit'] / 100. for key in pairs], color='red', label='first order', marker='.')
    axs[1, 0].plot(x, [data_merged['ESMF']['np'][fun][key]['mean_misfit'] / 100. for key in pairs], color='green', label='second order', marker='x')
    axs[1, 0].plot(x, [data_merged['ESMF']['rbf'][fun][key]['mean_misfit'] / 100. for key in pairs], color='blue', label='higher order', marker='D')
    # axs[1, 0].set_title('ESMF mean misfit')
    axs[1, 0].text(0.01, 0.99, "ESMF", transform=axs[1, 0].transAxes, fontsize=14, va='top', ha='left')
    axs[1, 1].plot(x, [data_merged['ESMF']['nn'][fun][key]['glob_cons_src'] for key in pairs], color='red', label='first order', marker='.')
    axs[1, 1].plot(x, [data_merged['ESMF']['np'][fun][key]['glob_cons_src'] for key in pairs], color='green', label='second order', marker='x')
    axs[1, 1].plot(x, [data_merged['ESMF']['rbf'][fun][key]['glob_cons_src'] for key in pairs], color='blue', label='higher order', marker='D')
    # axs[1, 1].set_title('ESMF global source conservation')
    axs[1, 1].text(0.01, 0.99, "ESMF", transform=axs[1, 1].transAxes, fontsize=14, va='top', ha='left')
    # YAC
    axs[2, 0].plot(x, [data_merged['YAC']['nn'][fun][key]['mean_misfit'] / 100. for key in pairs], color='red', label='first order', marker='.')
    axs[2, 0].plot(x, [data_merged['YAC']['np'][fun][key]['mean_misfit'] / 100. for key in pairs], color='green', label='second order', marker='x')
    axs[2, 0].plot(x, [data_merged['YAC']['rbf'][fun][key]['mean_misfit'] / 100. for key in pairs], color='blue', label='higher order', marker='D')
    # axs[2, 0].set_title('YAC mean misfit')
    axs[2, 0].text(0.01, 0.99, "YAC", transform=axs[2, 0].transAxes, fontsize=14, va='top', ha='left')
    axs[2, 1].plot(x, [data_merged['YAC']['nn'][fun][key]['glob_cons_src'] for key in pairs], color='red', label='first order', marker='.')
    axs[2, 1].plot(x, [data_merged['YAC']['np'][fun][key]['glob_cons_src'] for key in pairs], color='green', label='second order', marker='x')
    axs[2, 1].plot(x, [data_merged['YAC']['rbf'][fun][key]['glob_cons_src'] for key in pairs], color='blue', label='higher order', marker='D')
    # axs[2, 1].set_title('YAC global source conservation')
    axs[2, 1].text(0.01, 0.99, "YAC", transform=axs[2, 1].transAxes, fontsize=14, va='top', ha='left')
    # SCRIP
    axs[3, 0].plot(x, [data_merged['SCRIP']['nn'][fun][key]['mean_misfit'] / 100. for key in pairs], color='red', label='first order', marker='.')
    axs[3, 0].plot(x, [data_merged['SCRIP']['np'][fun][key]['mean_misfit'] / 100. for key in pairs], color='green', label='second order', marker='x')
    axs[3, 0].plot(x, [data_merged['SCRIP']['rbf'][fun][key]['mean_misfit'] / 100. for key in pairs], color='blue', label='higher order', marker='D')
    # axs[3, 0].set_title('SCRIP mean misfit')
    axs[3, 0].text(0.01, 0.99, "SCRIP", transform=axs[3, 0].transAxes, fontsize=14, va='top', ha='left')
    axs[3, 1].plot(x, [data_merged['SCRIP']['nn'][fun][key]['glob_cons_src'] for key in pairs], color='red', label='first order', marker='.')
    axs[3, 1].plot(x, [data_merged['SCRIP']['np'][fun][key]['glob_cons_src'] for key in pairs], color='green', label='second order', marker='x')
    axs[3, 1].plot(x, [data_merged['SCRIP']['rbf'][fun][key]['glob_cons_src'] for key in pairs], color='blue', label='higher order', marker='D')
    # axs[3, 1].set_title('SCRIP global source conservation')
    axs[3, 1].text(0.01, 0.99, "SCRIP", transform=axs[3, 1].transAxes, fontsize=14, va='top', ha='left')

    for ax in axs.flat:
        # ax.set(xlabel='x-label', ylabel='y-label')
        ax.set_xticks(x)
        ax.set_xticklabels(pairs, rotation=45, ha='right')
        legend = ax.legend(loc='upper right', frameon=False)
        legend.get_frame().set_facecolor('none')  # transparent background
        ax.set_yscale('log')
    for i in range(4):
        axs[i, 0].set(ylabel='mean misfit')
        if yrange_mean_misfit is not None:
            ylimits, yticks = yrange_mean_misfit
            axs[i, 0].set(ylim=ylimits, yticks=yticks)
        axs[i, 1].set(ylabel='global source conservation')
        if yrange_glob_cons_src is not None:
            ylimits, yticks = yrange_glob_cons_src
            axs[i, 1].set(ylim=ylimits, yticks=yticks)

    # Hide x labels and tick labels for top plots and y ticks for right plots.
    # for ax in axs.flat:
    # ax.label_outer()

    fig.tight_layout()
    fig.savefig(f'{save_path}/overview-{fun}.png')
    fig.show()

def gather_ylimits(data_base, data_cons, data_bad_torc, ref_data_base, ref_data_cons, pairs):
    fields = ["mean_misfit", "max_misfit", "rms_misfit", "l_min", "l_max", "glob_cons_src", "glob_cons_tgt"]
    ylimits = {}
    for field in fields: ylimits[field] = np.zeros(2)

    def gather_field_values(data, field):
        return np.array([data[res][mapping][fun][pair][field]
                         for res in data.keys()
                         for mapping in data[res].keys()
                         for fun in data[res][mapping].keys()
                         for pair in pairs])


    def gather_ref_field_values(data, field):
        return np.array([data[mapper][mapping][fun][pair][field]
                         for mapper in data.keys()
                         for mapping in data[mapper].keys()
                         for fun in data[mapper][mapping].keys()
                         for pair in pairs])

    def accumulate(acc_fun, base, cons, bad_torc, ref_base, ref_cons):
        return acc_fun(np.array([acc_fun(base), acc_fun(cons), acc_fun(bad_torc), acc_fun(ref_base), acc_fun(ref_cons)]))

    for field in fields:
        base_vals = gather_field_values(data_base, field)
        cons_vals = gather_field_values(data_cons, field)
        bad_torc_vals = gather_field_values(data_bad_torc, field)
        ref_base_vals = gather_ref_field_values(ref_data_base, field)
        ref_cons_vals = gather_ref_field_values(ref_data_cons, field)

        min_val = accumulate(np.min, base_vals, cons_vals, bad_torc_vals, ref_base_vals, ref_cons_vals)
        max_val = accumulate(np.max, base_vals, cons_vals, bad_torc_vals, ref_base_vals, ref_cons_vals)
        ylimits[field][0], ylimits[field][1] = min_val, max_val

    return ylimits