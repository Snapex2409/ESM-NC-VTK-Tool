from envt.tools.filter import *
from envt.tools.nc2vtk import *
from envt.tools.evaluate import *
from envt.tools.convert import *
import envt.nc_util.nc_wrapper as ncw
import argparse

def main():
    parser = argparse.ArgumentParser(description="NetCDF Tool for ESM data processing.")
    subparsers = parser.add_subparsers(dest="mode", required=True, help="Execution mode (view, plot, vtk).")

    # View mode
    view_parser = subparsers.add_parser("view", help="View metadata or variable data.")
    view_parser.add_argument("file", type=str, help="Path to the NetCDF file.")
    view_parser.add_argument("--data", choices=["lon", "lat", "clo", "cla"], help="View a specific variable.")

    # Plot mode
    plot_parser = subparsers.add_parser("plot", help="Plot mesh points.")
    plot_parser.add_argument("file", type=str, help="Path to the NetCDF file.")
    plot_parser.add_argument("--var", type=str, required=True, help="Variable name prefix (e.g., 'torc').")
    plot_parser.add_argument("-m", "--mask", type=str, help="Mask file path.", default=None)
    plot_parser.add_argument("-o", "--output", type=str, help="Output file path.")

    # VTK mode
    vtk_parser = subparsers.add_parser("vtk", help="Generate VTK unstructured grid.")
    vtk_parser.add_argument("file", type=str, help="Path to the NetCDF file. Can be VTK file if --conv is used.")
    vtk_parser.add_argument("--var", type=str, required=True, help="Variable name prefix (e.g., 'torc').")
    vtk_parser.add_argument("-c", "--corner", action="store_true", help="Use corner coordinates (clo/cla).")
    vtk_parser.add_argument("-m", "--mask", type=str, help="Mask file path.", default=None)
    vtk_parser.add_argument("-o", "--output", type=str, help="Output file path.", default=None)
    vtk_parser.add_argument("-f", "--filter", action="store_true", help="Filter out land cells")

    # VTK Convert mode
    vtkc_parser = subparsers.add_parser("vtkc", help="Convert VTK unstructured grid.")
    vtkc_parser.add_argument("file", type=str, help="Path to the VTK file.")
    vtkc_parser.add_argument("-cv23", "--conv23", action="store_true",
                             help="Convert 2D (lat/lon) file to 3D cartesian coordinates.")
    vtkc_parser.add_argument("-cv32", "--conv32", action="store_true",
                             help="Convert 3D cartesian coordinates file to 2D (lat/lon).")
    vtkc_parser.add_argument("-o", "--output", type=str, help="Output file path.", default=None)

    # VTK Evaluate mode
    vtke_parser = subparsers.add_parser("vtke", help="Evaluate VTK unstructured grid.")
    vtke_parser.add_argument("file", type=str, help="Path to the VTK file.")
    vtke_parser.add_argument("-f", "--function", required=True, type=str, help="Function to evaluate.",
                             default="sinusoid", choices=["sinusoid", "harmonic", "vortex", "golfstream"])
    vtke_parser.add_argument("-o", "--output", type=str, help="Output file path.", default=None)
    vtke_parser.add_argument("-d", "--diff", action="store_true",
                             help="Computes difference of VTK data to analytical solution")
    vtke_parser.add_argument("-s", "--source", type=str, help="Source mesh path. Only used in diff mode", default=None)

    # VTK filtering mode
    vtkf_parser = subparsers.add_parser("vtkf", help="Filter VTK unstructured grid.")
    vtkf_parser.add_argument("file", type=str, help="Path to the VTK file.")
    vtkf_parser.add_argument("nc_file", type=str, help="NetCDF file to process.")
    vtkf_parser.add_argument("var", type=str, help="Variable name prefix (e.g., 'torc').")
    vtkf_parser.add_argument("-o", "--output", type=str, help="Output file path.", default=None)
    vtkf_parser.add_argument("-w", "--water", action="store_true", help="Flag if mask value denotes water or not.")

    args = parser.parse_args()

    if args.mode == "view":
        nc_file = ncw.NCFile(args.file)
        if args.data is not None:
            nc_file.print_var_data(args.file, args.data)
        else:
            nc_file.print_overview()

    elif args.mode == "plot":
        nc_file = ncw.NCFile(args.file)
        out_path = "./plot.png"
        if args.output is not None: out_path = args.output
        nc_file.plot_var_centers(ncw.NCVars.get_entry(args.var), out_path, args.mask)

    elif args.mode == "vtk":
        conv = NC2VTK(args.file, args.mask)
        out_path = "./output.vtk"
        if args.output is not None: out_path = args.output
        conv.nc2vtk(ncw.NCVars.get_entry(args.var), out_path, args.filter, args.corner)

    elif args.mode == "vtkc":
        out_path = "./output.vtk"
        if args.output is not None: out_path = args.output
        conv = Converter(args.file, out_path)
        if args.conv23:
            conv.convert(Converter.Mode2DTO3D())
        else:
            conv.convert(Converter.Mode3DTO2D())

    elif args.mode == "vtke":
        out_path = "./output.vtk"
        if args.output is not None: out_path = args.output
        ev = Evaluator(args.file, out_path)
        if args.diff:
            ev.evaluate_diff(args.source, args.function)
        else:
            ev.evaluate(args.function)

    elif args.mode == "vtkf":
        out_path = "./output.vtk"
        if args.output is not None: out_path = args.output
        fil = Filter(args.file, ncw.NCVars.get_entry(args.var), args.nc_file)
        fil.apply(out_path, 0.001, args.water)


if __name__ == '__main__':
    main()