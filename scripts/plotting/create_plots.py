import numpy as np
import matplotlib.pyplot as plt

import scripts.plotting.util.io as io
from scripts.plotting.data_loaders.ReferenceMetrics import *
from scripts.plotting.data_loaders.Metrics import *
from scripts.plotting.util.plot_helpers import plot_data_field, plot_res_scaling, plot_data_field_merged, plot_data_field_merged_bar

if __name__ == '__main__':
    # load reference
    spec = RefMetrics.generateSpec(
        [RefMetrics.ESMF, RefMetrics.SCRIP, RefMetrics.YAC],
        {RefMetrics.ESMF: RefMetrics.ESMF_BASE,
                   RefMetrics.SCRIP: RefMetrics.SCRIP_BASE,
                   RefMetrics.YAC: RefMetrics.YAC_BASE
         }
    )
    csv_data = RefMetrics.loadCSV("../..", spec)
    ref_data = RefMetrics.rename(csv_data)

    # load our data
    use_cons = False
    bad_torc = False
    has_resolutions = True
    override_name = None
    data = Metrics.load("../../benchmark", use_cons, bad_torc, has_resolutions, override_name)


    data_merged = ref_data
    data_merged["preCICE"] = data[Metrics.resolutions[0]]
    savePath = "../../images/metrics_th0-80"
    pairs = ["torc-bggd", "torc-icos", "torc-sse7", "bggd-torc", "icos-torc", "sse7-torc", "nogt-bggd", "nogt-icos", "nogt-sse7", "bggd-nogt", "icos-nogt", "sse7-nogt"]
    plot_data_field_merged_bar(data_merged, "mean_misfit", {"nogt-icoh", "icos-icoh"}, True, savePath, True, pairs)
    plot_data_field_merged_bar(data_merged, "max_misfit", {"nogt-icoh", "icos-icoh"}, True, savePath, True, pairs)
    plot_data_field_merged_bar(data_merged, "rms_misfit", {"nogt-icoh", "icos-icoh"}, True, savePath, True, pairs)
    plot_data_field_merged_bar(data_merged, "l_min", {"nogt-icoh", "icos-icoh"}, False, savePath, False, pairs)
    plot_data_field_merged_bar(data_merged, "l_max", {"nogt-icoh", "icos-icoh"}, False, savePath, False, pairs)
    plot_data_field_merged_bar(data_merged, "glob_cons_src", {"nogt-icoh", "icos-icoh"}, True, savePath, True, pairs, False)
    plot_data_field_merged_bar(data_merged, "glob_cons_tgt", {"nogt-icoh", "icos-icoh"}, True, savePath, True, pairs)

    #for resolution in Metrics.resolutions:
    #    for mapping in Metrics.mappings:
    #        pass
            #plot_data_field(data[resolution][mapping], "mean_misfit", "TH: " + resolution + " Mapping: " + mapping,
            #                ref_data[RefMetrics.ESMF][mapping],
            #                {"nogt-icoh", "icos-icoh"}, "ESMF")
            #plot_data_field(data[resolution][mapping], "mean_misfit", "TH: " + resolution + " Mapping: " + mapping,
            #                ref_data[RefMetrics.SCRIP][mapping],
            #                {"nogt-icoh", "icos-icoh"}, "SCRIP")
    #        plot_data_field(data[resolution][mapping], "mean_misfit", "TH: " + resolution + " Mapping: " + mapping,
    #                        ref_data[RefMetrics.YAC][mapping],
    #                        {"nogt-icoh", "icos-icoh"}, "YAC")

    #plot_res_scaling(data, "mean_misfit", "nn", "gulfstream", "", ref_data[RefMetrics.ESMF][mapping],
    #                        {"nogt-icoh", "icos-icoh"})
    #plot_res_scaling(data, "max_misfit", "nn", "gulfstream", "", ref_data[RefMetrics.ESMF][mapping],
    #                 {"nogt-icoh", "icos-icoh"})

    exit(0)
    # N mappings x 3 orders x 4 mappers
    for fun in Metrics.fun_names:
        #fun = Metrics.fun_names[2]
        plt_data = np.zeros((len(pairs), 3, 4))
        order2idx = {'nn' : 0, 'np' : 1, 'rbf' : 2}
        mapper2idx = {'preCICE' : 0, 'ESMF' : 1, 'YAC' : 2, 'SCRIP' : 3}
        orders = ['nn', 'np', 'rbf']
        mappers = ['preCICE', 'ESMF', 'YAC', 'SCRIP']
        for order in orders:
            for mapper in mappers:
                factor = 100.
                #if mapper == 'preCICE': factor = 1.
                plt_data[:, order2idx[order], mapper2idx[mapper]] = np.array([data_merged[mapper][order][fun][key]['glob_cons_src'] for key in pairs]) / factor

        sample_labels = pairs
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
        n_categories = len(pairs)
        n_samples = 4
        x = np.arange(n_categories)
        width = 0.2  # Width of each sample group
        offsets = np.linspace(-width * (n_samples - 1) / 2,
                              width * (n_samples - 1) / 2,
                              n_samples)
        spacing = 0.01

        def plt_fig(current_orders, name=""):
            fig, ax = plt.subplots(figsize=(10, 4))
            for mapper in mappers:
                # bottom = np.zeros(len(sample_labels))
                # for order in ['rbf', 'np', 'nn']: # layer
                for order in current_orders:  # layer
                    values = plt_data[:, order2idx[order], mapper2idx[mapper]]
                    wfac = 1.0
                    if order == 'rbf': wfac = 2.0
                    ax.bar(x + offsets[mapper2idx[mapper]], values, width / wfac - spacing,
                           color=colors[mapper2idx[mapper]][order2idx[order]], label=f'{mapper} {order}')
                    # bottom += values

            ax.set_xticks(x)
            ax.set_xticklabels(pairs, rotation=45)
            ax.set_ylabel('Global Source Conservation')
            ax.set_title(f'{fun}')
            ax.set_ylim([0, 0.0006])
            #ax.legend(title='Layers')

            plt.tight_layout()
            if name != "": plt.savefig(f'images/{name}.png')
            plt.show()

        plt_fig(['nn'], f"glob-cons-src-scale-{fun}0")
        plt_fig(['nn', 'np'], f"glob-cons-src-scale-{fun}1")
        plt_fig(['nn', 'np', 'rbf'], f"glob-cons-src-scale-{fun}2")


    exit(0)
    # mean misfit and src cons
    x = np.arange(len(pairs))

    fun = Metrics.fun_names[2]
    fig, axs = plt.subplots(4, 2, figsize=(10, 12))
    #preCICE
    axs[0, 0].plot(x, [data_merged['preCICE']['nn'][fun][key]['mean_misfit'] for key in pairs], color='red', label='first order', marker='.')
    axs[0, 0].plot(x, [data_merged['preCICE']['np'][fun][key]['mean_misfit'] for key in pairs], color='green', label='second order', marker='x')
    axs[0, 0].plot(x, [data_merged['preCICE']['rbf'][fun][key]['mean_misfit'] for key in pairs], color='blue', label='higher order', marker='D')
    #axs[0, 0].set_title('preCICE mean misfit')
    axs[0, 0].text(0.01, 0.99, "preCICE", transform=axs[0, 0].transAxes, fontsize=14, va='top', ha='left')
    axs[0, 1].plot(x, [data_merged['preCICE']['nn'][fun][key]['glob_cons_src'] for key in pairs], color='red', label='first order', marker='.')
    axs[0, 1].plot(x, [data_merged['preCICE']['np'][fun][key]['glob_cons_src'] for key in pairs], color='green', label='second order', marker='x')
    axs[0, 1].plot(x, [data_merged['preCICE']['rbf'][fun][key]['glob_cons_src'] for key in pairs], color='blue', label='higher order', marker='D')
    #axs[0, 1].set_title('preCICE global source conservation')
    axs[0, 1].text(0.01, 0.99, "preCICE", transform=axs[0, 1].transAxes, fontsize=14, va='top', ha='left')
    #ESMF
    axs[1, 0].plot(x, [data_merged['ESMF']['nn'][fun][key]['mean_misfit'] / 100. for key in pairs], color='red', label='first order', marker='.')
    axs[1, 0].plot(x, [data_merged['ESMF']['np'][fun][key]['mean_misfit'] / 100. for key in pairs], color='green', label='second order', marker='x')
    axs[1, 0].plot(x, [data_merged['ESMF']['rbf'][fun][key]['mean_misfit'] / 100. for key in pairs], color='blue', label='higher order', marker='D')
    #axs[1, 0].set_title('ESMF mean misfit')
    axs[1, 0].text(0.01, 0.99, "ESMF", transform=axs[1, 0].transAxes, fontsize=14, va='top', ha='left')
    axs[1, 1].plot(x, [data_merged['ESMF']['nn'][fun][key]['glob_cons_src'] / 100. for key in pairs], color='red', label='first order', marker='.')
    axs[1, 1].plot(x, [data_merged['ESMF']['np'][fun][key]['glob_cons_src'] / 100. for key in pairs], color='green', label='second order', marker='x')
    axs[1, 1].plot(x, [data_merged['ESMF']['rbf'][fun][key]['glob_cons_src'] / 100. for key in pairs], color='blue', label='higher order', marker='D')
    #axs[1, 1].set_title('ESMF global source conservation')
    axs[1, 1].text(0.01, 0.99, "ESMF", transform=axs[1, 1].transAxes, fontsize=14, va='top', ha='left')
    #YAC
    axs[2, 0].plot(x, [data_merged['YAC']['nn'][fun][key]['mean_misfit'] / 100. for key in pairs], color='red', label='first order', marker='.')
    axs[2, 0].plot(x, [data_merged['YAC']['np'][fun][key]['mean_misfit'] / 100. for key in pairs], color='green', label='second order', marker='x')
    axs[2, 0].plot(x, [data_merged['YAC']['rbf'][fun][key]['mean_misfit'] / 100. for key in pairs], color='blue', label='higher order', marker='D')
    #axs[2, 0].set_title('YAC mean misfit')
    axs[2, 0].text(0.01, 0.99, "YAC", transform=axs[2, 0].transAxes, fontsize=14, va='top', ha='left')
    axs[2, 1].plot(x, [data_merged['YAC']['nn'][fun][key]['glob_cons_src'] / 100. for key in pairs], color='red', label='first order', marker='.')
    axs[2, 1].plot(x, [data_merged['YAC']['np'][fun][key]['glob_cons_src'] / 100. for key in pairs], color='green', label='second order', marker='x')
    axs[2, 1].plot(x, [data_merged['YAC']['rbf'][fun][key]['glob_cons_src'] / 100. for key in pairs], color='blue', label='higher order', marker='D')
    #axs[2, 1].set_title('YAC global source conservation')
    axs[2, 1].text(0.01, 0.99, "YAC", transform=axs[2, 1].transAxes, fontsize=14, va='top', ha='left')
    #SCRIP
    axs[3, 0].plot(x, [data_merged['SCRIP']['nn'][fun][key]['mean_misfit'] / 100. for key in pairs], color='red', label='first order', marker='.')
    axs[3, 0].plot(x, [data_merged['SCRIP']['np'][fun][key]['mean_misfit'] / 100. for key in pairs], color='green', label='second order', marker='x')
    axs[3, 0].plot(x, [data_merged['SCRIP']['rbf'][fun][key]['mean_misfit'] / 100. for key in pairs], color='blue', label='higher order', marker='D')
    #axs[3, 0].set_title('SCRIP mean misfit')
    axs[3, 0].text(0.01, 0.99, "SCRIP", transform=axs[3, 0].transAxes, fontsize=14, va='top', ha='left')
    axs[3, 1].plot(x, [data_merged['SCRIP']['nn'][fun][key]['glob_cons_src'] / 100. for key in pairs], color='red', label='first order', marker='.')
    axs[3, 1].plot(x, [data_merged['SCRIP']['np'][fun][key]['glob_cons_src'] / 100. for key in pairs], color='green', label='second order', marker='x')
    axs[3, 1].plot(x, [data_merged['SCRIP']['rbf'][fun][key]['glob_cons_src'] / 100. for key in pairs], color='blue', label='higher order', marker='D')
    #axs[3, 1].set_title('SCRIP global source conservation')
    axs[3, 1].text(0.01, 0.99, "SCRIP", transform=axs[3, 1].transAxes, fontsize=14, va='top', ha='left')

    for ax in axs.flat:
        #ax.set(xlabel='x-label', ylabel='y-label')
        ax.set_xticks(x)
        ax.set_xticklabels(pairs, rotation=45, ha='right')
        legend = ax.legend(loc='upper right', frameon=False)
        legend.get_frame().set_facecolor('none')  # transparent background
        ax.set_yscale('log')
    for i in range(4):
        axs[i, 0].set(ylabel='mean misfit')
        axs[i, 1].set(ylabel='global source conservation')


    # Hide x labels and tick labels for top plots and y ticks for right plots.
    #for ax in axs.flat:
        #ax.label_outer()

    fig.tight_layout()
    fig.show()