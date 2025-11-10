from data_loaders.ReferenceMetrics import *
from data_loaders.Metrics import *
from util.plot_helpers import plot_data_field_merged_bar, create_overlapped_bar_plots, create_overview_plot, gather_ylimits
from util.io import makedirs
import numpy as np

def load_ref_base():
    spec = RefMetrics.generateSpec(
        [RefMetrics.ESMF, RefMetrics.SCRIP, RefMetrics.YAC],
        {RefMetrics.ESMF: RefMetrics.ESMF_BASE,
         RefMetrics.SCRIP: RefMetrics.SCRIP_BASE,
         RefMetrics.YAC: RefMetrics.YAC_BASE
         }
    )
    csv_data = RefMetrics.loadCSV("../..", spec)
    return RefMetrics.rename(csv_data)

def load_ref_cons():
    spec = RefMetrics.generateSpec(
        [RefMetrics.ESMF, RefMetrics.SCRIP, RefMetrics.YAC],
        {RefMetrics.ESMF: RefMetrics.ESMF_CONS_FR,
         RefMetrics.SCRIP: RefMetrics.SCRIP_CONS_FR,
         RefMetrics.YAC: RefMetrics.YAC_CONS_FR
         }
    )
    csv_data = RefMetrics.loadCSV("../..", spec)
    return RefMetrics.rename(csv_data)

def create_merged_plots(data_merged, pairs, save_path, ylimits):
    plot_data_field_merged_bar(data_merged, "mean_misfit", {"nogt-icoh", "icos-icoh"}, True, save_path, True, pairs, yrange=ylimits["mean_misfit"])
    plot_data_field_merged_bar(data_merged, "max_misfit", {"nogt-icoh", "icos-icoh"}, True, save_path, True, pairs, yrange=ylimits["max_misfit"])
    plot_data_field_merged_bar(data_merged, "rms_misfit", {"nogt-icoh", "icos-icoh"}, True, save_path, True, pairs, yrange=ylimits["rms_misfit"])
    plot_data_field_merged_bar(data_merged, "l_min", {"nogt-icoh", "icos-icoh"}, False, save_path, False, pairs, yrange=ylimits["l_min"])
    plot_data_field_merged_bar(data_merged, "l_max", {"nogt-icoh", "icos-icoh"}, False, save_path, False, pairs, yrange=ylimits["l_max"])
    plot_data_field_merged_bar(data_merged, "glob_cons_src", {"nogt-icoh", "icos-icoh"}, True, save_path, True, pairs, yrange=ylimits["glob_cons_src"])
    plot_data_field_merged_bar(data_merged, "glob_cons_tgt", {"nogt-icoh", "icos-icoh"}, True, save_path, True, pairs, yrange=ylimits["glob_cons_tgt"])



if __name__ == '__main__':
    pairs = ["torc-bggd", "torc-icos", "torc-sse7", "bggd-torc",
             "icos-torc", "sse7-torc", "nogt-bggd", "nogt-icos",
             "nogt-sse7", "bggd-nogt", "icos-nogt", "sse7-nogt"]
    ref_data_base = load_ref_base()
    ref_data_cons = load_ref_cons()

    data_base = Metrics.load("../../benchmark", False, False, True, override_resolutions=["0_001"])
    data_cons = Metrics.load("../../benchmark", True, False, True, None, override_resolutions=["0_001"])
    data_bad_torc = Metrics.load("../../benchmark", False, True, False, None)

    # setting up y axis for all plots
    #print(gather_ylimits(data_base, data_cons, data_bad_torc, ref_data_base, ref_data_cons, pairs)) # this is just some information about the actual data
    ylimits = {}
    ylimits["mean_misfit"]   = (np.array([5e-7, 5e-1]), np.array([1e-7, 1e-5, 1e-3, 1e-1]))
    ylimits["max_misfit"]    = (np.array([5e-5, 2e-0]), np.array([1e-5, 1e-3, 1e-1, 1e-0]))
    ylimits["rms_misfit"]    = (np.array([1e-6, 1e-1]), np.array([1e-6, 1e-4, 1e-2, 1e-1]))
    ylimits["l_min"]         = None
    ylimits["l_max"]         = None
    ylimits["glob_cons_src"] = (np.array([1e-7, 1e-3]), np.array([1e-7, 1e-5, 1e-3]))
    ylimits["glob_cons_tgt"] = (np.array([1e-10, 1e-1]), np.array([1e-10, 1e-7, 1e-4, 1e-1]))
    function = "gulfstream" # sinusoid harmonic vortex gulfstream

    # base mappings both
    for resolution in data_base.keys():
        save_path = f"../../images/metrics/{resolution}"
        makedirs(save_path)
        data_merged = ref_data_base
        data_merged["preCICE"] = data_base[resolution]
        create_merged_plots(data_merged, pairs, save_path, ylimits)
        create_overlapped_bar_plots(data_merged, "mean_misfit", pairs, save_path, True, True, yrange=ylimits["mean_misfit"])
        create_overlapped_bar_plots(data_merged, "glob_cons_src", pairs, save_path, True, False, yrange=ylimits["glob_cons_src"])
        create_overview_plot(data_merged, pairs, function, save_path, ylimits["mean_misfit"], ylimits["glob_cons_src"])

    # cons mapping preCICE, base reference
    for resolution in data_cons.keys():
        save_path = f"../../images/metrics_cons/{resolution}"
        makedirs(save_path)
        data_merged = ref_data_base
        data_merged["preCICE"] = data_cons[resolution]
        create_merged_plots(data_merged, pairs, save_path, ylimits)
        create_overlapped_bar_plots(data_merged, "mean_misfit", pairs, save_path, True, True, yrange=ylimits["mean_misfit"])
        create_overlapped_bar_plots(data_merged, "glob_cons_src", pairs, save_path, True, False, yrange=ylimits["glob_cons_src"])
        create_overview_plot(data_merged, pairs, function, save_path, ylimits["mean_misfit"], ylimits["glob_cons_src"])

    # cons mapping both
    for resolution in data_cons.keys():
        save_path = f"../../images/metrics_cons_both/{resolution}"
        makedirs(save_path)
        data_merged = ref_data_cons
        data_merged["preCICE"] = data_cons[resolution]
        create_merged_plots(data_merged, pairs, save_path, ylimits)
        create_overlapped_bar_plots(data_merged, "mean_misfit", pairs, save_path, True, True, yrange=ylimits["mean_misfit"])
        create_overlapped_bar_plots(data_merged, "glob_cons_src", pairs, save_path, True, False, yrange=ylimits["glob_cons_src"])
        create_overview_plot(data_merged, pairs, function, save_path, ylimits["mean_misfit"], ylimits["glob_cons_src"])

    # bad torc, base both
    save_path = f"../../images/metrics_bad_torc"
    makedirs(save_path)
    data_merged = ref_data_base
    data_merged["preCICE"] = data_bad_torc[list(data_bad_torc.keys())[0]]
    create_merged_plots(data_merged, pairs, save_path, ylimits)
    create_overlapped_bar_plots(data_merged, "mean_misfit", pairs, save_path, True, True, yrange=ylimits["mean_misfit"])
    create_overlapped_bar_plots(data_merged, "glob_cons_src", pairs, save_path, True, False, yrange=ylimits["glob_cons_src"])
    create_overview_plot(data_merged, pairs, function, save_path, ylimits["mean_misfit"], ylimits["glob_cons_src"])
