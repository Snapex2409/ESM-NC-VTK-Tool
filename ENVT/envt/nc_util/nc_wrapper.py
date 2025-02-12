import netCDF4 as nc
from enum import Enum
import matplotlib.pyplot as plt

class NCVars(Enum):
    BGGD = "bggd",
    ICOH = "icoh",
    ICOS = "icos",
    NOGT = "nogt",
    SSE7 = "sse7",
    SSEA = "ssea",
    TORC = "torc"

    def __str__(self):
        return self.value

    @staticmethod
    def get_entry(name):
        inv_map = {v:n for n,v in NCVars.__dict__.items()}
        return inv_map[name]


class NCFile:
    def __init__(self, path):
        self.path = path
        with nc.Dataset(path, 'r') as ds:
            self.dimensions = ds.dimensions
            self.variables = ds.variables
            self.attributes = ds.ncattrs()
            self.dataset = ds

    def var_lon_data(self, var:NCVars):
        name = f"{var.value}.lon"
        lon = self.variables[name][:]
        return lon

    def var_lat_data(self, var:NCVars):
        name = f"{var.value}.lat"
        lat = self.variables[name][:]
        return lat

    def var_clo_data(self, var:NCVars):
        name = f"{var.value}.clo"
        clo = self.variables[name][:]
        return clo

    def var_cla_data(self, var:NCVars):
        name = f"{var.value}.cla"
        cla = self.variables[name][:]
        return cla

    def var_msk_data(self, var:NCVars):
        name = f"{var.value}.msk"
        msk = self.variables[name][:]
        return msk

    def print_overview(self):
        print(f"NetCDF File: {self.path}")

        print("\nDimensions:")
        for dim_name, dim in self.dimensions.items():
            print(f"  {dim_name}: size = {len(dim)}")

        print("\nVariables:")
        for var_name, var in self.variables.items():
            print(f"  {var_name}:")
            print(f"    Dimensions: {var.dimensions}")
            print(f"    Shape: {var.shape}")
            print(f"    Attributes:")
            for attr_name in var.ncattrs():
                print(f"      {attr_name}: {getattr(var, attr_name)}")

        print("\nGlobal Attributes:")
        for attr_name in self.attributes:
            print(f"  {attr_name}: {getattr(self.dataset, attr_name)}")

    def print_var_data(self, var, limit=100):
        if var in self.variables:
            data = self.variables[var][:]
            print(f"Data for variable '{var}':")
            print(f"Shape: {data.shape}")
            print(f"Type: {data.dtype}")

            # If the data is large, show only a snippet
            if data.size > limit >= 0:
                print("Data (snippet):")
                print(data.ravel()[:100])  # Show the first 100 values
                print("...")
            else:
                print("Data:")
                print(data)
        else:
            print(f"Variable '{var}' not found in the file.")

    def plot_var_centers(self, var:NCVars, outpath, mask_path=None):
        lon_var_name = f"{var.value}.lon"
        lat_var_name = f"{var.value}.lat"
        mask_var_name = f"{var.value}.msk"
        use_mask = mask_path is not None

        lon = self.variables[lon_var_name][:]
        lat = self.variables[lat_var_name][:]
        msk = NCFile(outpath).variables[mask_var_name][:] if use_mask else None

        # Flatten arrays to extract all points
        lon = lon.flatten()
        lat = lat.flatten()
        if use_mask: msk = msk.flatten()

        plt.figure(figsize=(10, 6))
        if use_mask:
            plt.scatter(lon, lat, s=1, c=msk, alpha=0.7)
        else:
            plt.scatter(lon, lat, s=1, c='blue', alpha=0.7)
        position = "Centers"
        plt.title(f"Scatter Plot of Mesh Point {position} ({var.value})")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.grid(True)
        plt.savefig(outpath)
