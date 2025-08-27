from collections import defaultdict
import csv

class RefMetrics:
    SCRIP = "SCRIP"
    ESMF = "ESMF"
    XIOS = "XIOS"
    YAC = "YAC"
    Couplers = [SCRIP, ESMF, XIOS, YAC]
    Mappings = {
        SCRIP : ["-L_CONS2ND_FRACAREA", "-L_CONSERV_DESTAREA", "-L_CONSERV_FRACAREA", "_BICUBIC", "_BILINEAR", "_CONS2ND_FRACAREA", "_CONSERV_DESTAREA", "_CONSERV_FRACAREA", "_DISTWGT_1"],
        ESMF : ["-820bs08-U_CONS2ND_FRACAREA", "-820bs08-U_CONSERV_DESTAREA", "-820bs08-U_CONSERV_FRACAREA", "-820bs08_BICUBIC", "-820bs08_BILINEAR", "-820bs08_CONSERV_DESTAREA", "-820bs08_DISTWGT_1"],
        XIOS : ["_CONS2ND_FRACAREA", "_CONSERV_DESTAREA", "_CONSERV_FRACAREA"],
        YAC : ["_BICUBIC", "_BILINEAR", "_CONS2ND_FRACAREA", "_CONSERV_DESTAREA", "_CONSERV_FRACAREA", "_DISTWGT_1"]
    }
    SCRIP_BASE = ["_BICUBIC", "_BILINEAR", "_DISTWGT_1"]
    ESMF_BASE = ["-820bs08_BICUBIC", "-820bs08_BILINEAR", "-820bs08_DISTWGT_1"]
    XIOS_BASE = []
    YAC_BASE = ["_BICUBIC", "_BILINEAR", "_DISTWGT_1"]

    SCRIP_CONS_FR = ["_CONS2ND_FRACAREA", "_CONSERV_FRACAREA", "_DISTWGT_1"]
    ESMF_CONS_FR = ["-820bs08-U_CONS2ND_FRACAREA", "-820bs08-U_CONSERV_FRACAREA", "-820bs08_DISTWGT_1"]
    XIOS_CONS_FR = ["_CONS2ND_FRACAREA", "_CONSERV_FRACAREA", "_DISTWGT_1"]
    YAC_CONS_FR = ["_CONS2ND_FRACAREA", "_CONSERV_FRACAREA", "_DISTWGT_1"]

    Functions = ["classic", "gulfstream", "harmonic", "vortex"]

    @staticmethod
    def generateSpec(coupler=None, mapping=None, function=None):
        spec = defaultdict()

        if coupler is not None: spec["coupler"] = coupler
        else: spec["coupler"] = RefMetrics.Couplers

        if mapping is not None: spec["mapping"] = mapping
        else: spec["mapping"] = RefMetrics.Mappings

        if function is not None: spec["function"] = function
        else: spec["function"] = RefMetrics.Functions

        return spec

    @staticmethod
    def loadCSV(base_path, specification):
        result = {}

        for coupler in specification["coupler"]:
            result[coupler] = {}
            for mapping in specification["mapping"][coupler]:
                result[coupler][mapping] = {}
                for function in specification["function"]:
                    result[coupler][mapping][function] = []

                    file_name = f"{base_path}/data/ref_metrics/{coupler}{mapping}_{function}.csv"
                    with open(file_name, "r") as file:
                        reader = csv.reader(file)  # Reads as dictionaries
                        lines = [l[0] for l in reader]

                        #figure out order
                        names = lines[0][1:].split(';')

                        for line in lines[1:]:
                            entry = {}
                            line_data = line.split(';')
                            for i in range(len(line_data)):
                                entry[names[i]] = line_data[i]

                            result[coupler][mapping][function].append(entry)

        return result

    @staticmethod
    def rename(csv_data):
        renaming = {"mean_misfit": "Mean misfit", "max_misfit": "Max misfit", "rms_misfit": "Rms misfit",
                    "l_min": "Lmin", "l_max": "Lmax", "glob_cons_src": "Glob Cons Src",
                    "glob_cons_tgt": "Glob Cons Dst"}
        mapping_rename = {"-L_CONS2ND_FRACAREA" : "rbf", "-L_CONSERV_DESTAREA" : "np", "-L_CONSERV_FRACAREA" : "np", "_BICUBIC" : "rbf", "_BILINEAR" : "np", "_CONS2ND_FRACAREA" : "rbf", "_CONSERV_DESTAREA" : "np", "_CONSERV_FRACAREA" : "np", "_DISTWGT_1" : "nn",
                "-820bs08-U_CONS2ND_FRACAREA" : "rbf", "-820bs08-U_CONSERV_DESTAREA" : "np", "-820bs08-U_CONSERV_FRACAREA" : "np", "-820bs08_BICUBIC" : "rbf", "-820bs08_BILINEAR" : "np", "-820bs08_CONSERV_DESTAREA" : "np", "-820bs08_DISTWGT_1" : "nn",
                "_CONS2ND_FRACAREA" : "rbf", "_CONSERV_DESTAREA" : "np", "_CONSERV_FRACAREA" : "np",
                "_BICUBIC" : "rbf", "_BILINEAR" : "np", "_CONS2ND_FRACAREA" : "rbf", "_CONSERV_DESTAREA" : "np", "_CONSERV_FRACAREA" : "np", "_DISTWGT_1" : "nn"}
        function_rename = {"classic": "sinusoid", "gulfstream": "gulfstream", "harmonic": "harmonic",
                           "vortex": "vortex"}
        ref_data = {}
        for coupler in csv_data.keys():
            ref_data[coupler] = dict()
            for mapping in csv_data[coupler].keys():
                ref_data[coupler][mapping_rename[mapping]] = dict()
                for fn in csv_data[coupler][mapping].keys():
                    ref_data[coupler][mapping_rename[mapping]][function_rename[fn]] = dict()
                    for entry in csv_data[coupler][mapping][fn]:
                        tmp = {}
                        for name in renaming.keys():
                            if renaming[name] in entry.keys():
                                tmp[name] = float(entry[renaming[name]])
                            else:
                                tmp[name] = 0.0
                        ref_data[coupler][mapping_rename[mapping]][function_rename[fn]][entry['grid pair']] = tmp

        return ref_data