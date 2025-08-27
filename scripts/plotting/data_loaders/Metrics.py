import scripts.plotting.util.io as io

class Metrics:
    SEA_NAMES = ["nogt", "torc"]
    ATM_NAMES = ["bggd", "icoh", "icos", "sse7", "ssea"]
    FUN_NAMES = ["gulfstream", "harmonic", "sinusoid", "vortex"]

    default_resolutions = ["0_2", "0_8"]
    default_resolutions_numeric = [0.2, 0.8]
    default_mapping_methods = ["nn", "np", "rbf"]
    default_meshes = ["nogt", "torc", "bggd", "icoh", "icos", "sse7", "ssea"]

    blank_data = {'mean_misfit': 0.0, 'max_misfit': 0.0, 'rms_misfit': 0.0, 'l_min': 0.0, 'l_max': 0.0,
                  'glob_cons_src': 0.0, 'glob_cons_tgt': 0.0}

    @staticmethod
    def combine(mesh_src, mesh_dst):
        if mesh_src in Metrics.ATM_NAMES and mesh_dst in Metrics.ATM_NAMES:
            part_src = mesh_src + "_masked_by_nogt"
            part_dst = mesh_dst + "_masked_by_nogt"
        elif mesh_src in Metrics.ATM_NAMES and mesh_dst not in Metrics.ATM_NAMES:
            part_src = mesh_src + "_masked_by_" + mesh_dst
            part_dst = mesh_dst
        elif mesh_src not in Metrics.ATM_NAMES and mesh_dst in Metrics.ATM_NAMES:
            part_src = mesh_src
            part_dst = mesh_dst + "_masked_by_" + mesh_src
        else:
            part_src = mesh_src
            part_dst = mesh_dst
        return part_src + "_to_" + part_dst

    @staticmethod
    def create_structure(
            resolutions=default_resolutions,
            mapping_methods=default_mapping_methods,
            functions=FUN_NAMES,
            meshes=default_meshes
    ):
        buffer = dict()
        if resolutions is None: resolutions = Metrics.default_resolutions
        if mapping_methods is None: mapping_methods = Metrics.default_mapping_methods
        if functions is None: functions = Metrics.FUN_NAMES
        if meshes is None: meshes = Metrics.default_meshes

        for resolution in resolutions:
            buffer[resolution] = dict()
            for mapping in mapping_methods:
                buffer[resolution][mapping] = dict()
                for fun_name in functions:
                    buffer[resolution][mapping][fun_name] = dict()
                    for m1 in meshes:
                        for m2 in meshes:
                            if m1 == m2: continue
                            buffer[resolution][mapping][fun_name][m1 + "-" + m2] = Metrics.blank_data

        return buffer

    @staticmethod
    def load(benchmark_output_path, use_cons=False, bad_torc=False, has_resolutions=False,
             override_name=None, override_resolutions=None, override_mapping_methods=None,
             override_functions=None, override_meshes=None):
        buffer = Metrics.create_structure(override_resolutions, override_mapping_methods, override_functions, override_meshes)
        met_dir_name = "06_metrics"
        if bad_torc: met_dir_name = met_dir_name + "_bad_torc"
        if use_cons: met_dir_name = met_dir_name + "_cons"
        if override_name is not None: met_dir_name = override_name

        resolutions = Metrics.default_resolutions if override_resolutions is None else override_resolutions
        mapping_methods = Metrics.default_mapping_methods if override_mapping_methods is None else override_mapping_methods
        functions = Metrics.FUN_NAMES if override_functions is None else override_functions
        meshes = Metrics.default_meshes if override_meshes is None else override_meshes

        def load_mesh_pairs(data_dir, resolution, mapping):
            for m1 in meshes:
                for m2 in meshes:
                    if m1 == m2: continue

                    for fun_name in functions:
                        filename = Metrics.combine(m1, m2) + "_" + fun_name + ".txt"
                        path = data_dir + "/" + filename
                        data = io.read_json(path)
                        if data is None: data = Metrics.blank_data
                        buffer[resolution][mapping][fun_name][m1 + "-" + m2] = data

        if has_resolutions:
            for resolution in resolutions:
                for mapping in mapping_methods:
                    data_dir = f"{benchmark_output_path}/{met_dir_name}/TH{resolution}/{mapping}"
                    load_mesh_pairs(data_dir, resolution, mapping)
        else:
            for mapping in mapping_methods:
                data_dir = f"{benchmark_output_path}/{met_dir_name}/{mapping}"
                load_mesh_pairs(data_dir, resolutions[0], mapping)

        return buffer
