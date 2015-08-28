import yaml
import argparse
import math
import sys

from scipy import interpolate
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
import numpy as np

class TerrainData(object):
    """
    Class representing Terrain data (terrain, rivers, aproximation, etc)
    """
    def __init__(self, yaml_file_name):
        """Constructor of TerrainData"""
        super(TerrainData, self).__init__()
        self.yaml_file_name = yaml_file_name
        self.conf = {} # Configuration loaded from yaml file
        self.terrain_data = [] # Terrain data list of tuples (3d coordinates)
        self.point_count = 0
        self.tck = {} # Patches of b-spline surface
        self.tX = None #
        self.tY = None # Terrain X,Y,Z cache for numpy API
        self.tZ = None #
        self.tW = None # Visualization purpose
        self.min_x = -sys.maxsize
        self.max_x = sys.maxsize
        self.min_y = -sys.maxsize
        self.max_y = sys.maxsize
        self.size_x = 0
        self.size_y = 0
        self.diff_x = 0.0
        self.diff_y = 0.0
        self.dx = 0.0
        self.dy = 0.0
        self.grid = {} # Cache for bilinear interpolation
        self.rivers_data_2d = {}
        self.rivers_data_3d = {}
        self.area_borders_2d = {}
        self.area_borders_3d = {}

    def load_conf_from_yaml(self):
        """
        Load configuration form yaml file
        """
        with open(self.yaml_file_name, 'r') as yaml_file:
            self.conf = yaml.load(yaml_file)

    def __post_process_terrain_data(self):
        """
        Try to postprocess terrain data
        """
        self.point_count = len(self.terrain_data)
        self.tX = [item[0] for item in self.terrain_data]
        self.tY = [item[1] for item in self.terrain_data]
        self.tZ = [item[2] for item in self.terrain_data]

        def find_first_different(array):
            """Find index of first different item"""
            index = 1
            first = array[0]
            while array[index] == first:
                index += 1
            index -= 1
            if index < len(array):
                return index
            else:
                return -1

        def find_first_same(array):
            """Find index of first same item"""
            index = 1
            first = array[0]
            while array[index] != first:
                index += 1
            index -= 1
            if index < len(array):
                return index
            else:
                return -1

        self.min_x = min(self.tX)
        self.max_x = max(self.tX)
        self.min_y = min(self.tY)
        self.max_y = max(self.tY)
        # Try to compute size of 2d array accordin repeated values
        if self.tX[0] == self.tX[1]:
            self.size_x = find_first_different(self.tX) + 1
        else:
            self.size_x = find_first_same(self.tX) + 1
        self.size_y = self.point_count / self.size_x
        self.diff_x = self.max_x - self.min_x
        self.diff_y = self.max_y - self.min_y
        self.dx = self.diff_x / float(self.size_x - 1)
        self.dy = self.diff_y / float(self.size_y - 1)
        self.grid = {}
        #print size_x, size_y, diff_x, diff_y, dx, dy
        for index in range(0, self.point_count):
            i = int( math.floor( (self.terrain_data[index][0] - self.min_x) / self.dx ) )
            j = int( math.floor( (self.terrain_data[index][1] - self.min_y) / self.dy ) )
            self.grid[(i, j)] = (self.terrain_data[index][0], self.terrain_data[index][1], self.terrain_data[index][2])

    def load_terrain(self):
        """
        Try to load data of terain
        """
        with open(self.conf['terrain'], 'r') as data_file:
            for line in data_file:
                self.terrain_data.append( tuple( float(item) for item in line.split() ) )
        self.__post_process_terrain_data()

    def load_rivers(self):
        """
        Try to load data of rivers
        """
        with open(self.conf['rivers'], 'r') as data_file:
            for line in data_file:
                items = line.split()
                river_id = int(items[-1])
                river_coord = (float(items[0]), float(items[1]))
                try:
                    river = self.rivers_data_2d[river_id]
                except KeyError:
                    river = self.rivers_data_2d[river_id] = []
                river.append(river_coord)

    def load_area(self):
        """
        Try to load definition of area border
        """
        with open(self.conf['area'], 'r') as area_file:
            self.area_borders_2d[0] = []
            for line in area_file:
                items = line.split()
                # Only one border ATM
                self.area_borders_2d[0].append( tuple( float(item) for item in items[1:]) )

    def aproximate_terrain(self):
        """
        Try to aproximate terrain with bspline surface
        """
        # dx = (self.size_x / 2) * self.dx
        # dy = (self.size_y / 2) * self.dy
        # tot_fp = 0

        # X = []
        # Y = []
        # Z = []
        # for i in range(0, self.size_x/2 + 2):
        #     for j in range(0, self.size_y/2 + 2):
        #         X.append(self.grid[(i,j)][0])
        #         Y.append(self.grid[(i,j)][1])
        #         Z.append(self.grid[(i,j)][2])
        # # kx an ky are degrees of polynoms
        # # s is smoothness
        # tck,fp,ior,msg = interpolate.bisplrep(X, Y, Z, kx=5, ky=5, full_output=1)
        # self.tck[(self.min_x, self.min_y, self.min_x + dx, self.min_y + dy)] = tck
        # tot_fp += fp
        # print tck, fp

        # X = []
        # Y = []
        # Z = []
        # for i in range(self.size_x/2 - 2, self.size_x):
        #     for j in range(0, self.size_y/2 + 2):
        #         X.append(self.grid[(i,j)][0])
        #         Y.append(self.grid[(i,j)][1])
        #         Z.append(self.grid[(i,j)][2])
        # tck,fp,ior,msg = interpolate.bisplrep(X, Y, Z, kx=5, ky=5, full_output=1)
        # self.tck[(self.min_x + dx, self.min_y, self.max_x, self.min_y + dy)] = tck
        # tot_fp += fp
        # print tck, fp

        # X = []
        # Y = []
        # Z = []
        # for i in range(0, self.size_x/2 + 2):
        #     for j in range(self.size_y/2 - 2, self.size_y):
        #         X.append(self.grid[(i,j)][0])
        #         Y.append(self.grid[(i,j)][1])
        #         Z.append(self.grid[(i,j)][2])
        # tck,fp,ior,msg = interpolate.bisplrep(X, Y, Z, kx=5, ky=5, full_output=1)
        # self.tck[(self.min_x, self.min_y + dy, self.min_x + dx, self.max_y)] = tck
        # tot_fp += fp
        # print tck, fp

        # X = []
        # Y = []
        # Z = []
        # for i in range(self.size_x/2 - 2, self.size_x):
        #     for j in range(self.size_y/2 - 2, self.size_y):
        #         X.append(self.grid[(i,j)][0])
        #         Y.append(self.grid[(i,j)][1])
        #         Z.append(self.grid[(i,j)][2])
        # tck,fp,ior,msg = interpolate.bisplrep(X, Y, Z, kx=5, ky=5, full_output=1)
        # self.tck[(self.min_x + dx, self.min_y + dy, self.max_x, self.max_y)] = tck
        # tot_fp += fp
        # print tck, fp

        tck,fp,ior,msg = interpolate.bisplrep(self.tX, self.tY, self.tZ, kx=5, ky=5, full_output=1)
        self.tck[(self.min_x, self.min_y, self.max_x, self.max_y)] = tck
        # Compute difference between original terrain data and b-spline surface
        self.tW = [abs(it[2] - interpolate.bisplev(it[0], it[1], tck)) for it in self.terrain_data]
        print tck
        print fp

    def aproximate_2d_borders(self):
        """
        Try to aproximate z coordinates of borders using terrain data
        """
        
        for border_id,border_2d in self.area_borders_2d.items():
            self.area_borders_3d[border_id] = []
            for bp in border_2d:
                # Compute indexes to the grid first
                i = int(math.floor( (bp[0] - self.min_x) / self.dx ))
                j = int(math.floor( (bp[1] - self.min_y) / self.dy ))
                # Compute weights for bilineral intebpolation
                kx = (bp[0] - (self.min_x + self.dx * i)) / self.dx
                ky = (bp[1] - (self.min_y + self.dy * j)) / self.dy
                z1 = self.grid[(i, j)][2]
                z2 = self.grid[(i + 1, j)][2]
                z3 = self.grid[(i, j + 1)][2]
                z4 = self.grid[(i + 1, j + 1)][2]
                z12 = (1.0 - kx) * z1 + kx * z2
                z34 = (1.0 - kx) * z3 + kx * z4
                Z = (1.0 - ky) * z12 + ky * z34
                self.area_borders_3d[border_id].append( (bp[0], bp[1], Z) )


    def aproximate_2d_rivers(self):
        """
        Try to aproximate z coordinates of rivers using terrain data
        """
        
        for river_id,river2d in self.rivers_data_2d.items():
            self.rivers_data_3d[river_id] = []
            last_z = sys.maxsize
            for rp in river2d:
                # Compute indexes to the grid first
                i = int(math.floor( (rp[0] - self.min_x) / self.dx ))
                j = int(math.floor( (rp[1] - self.min_y) / self.dy ))
                # Compute weights for bilineral interpolation
                kx = (rp[0] - (self.min_x + self.dx * i)) / self.dx
                ky = (rp[1] - (self.min_y + self.dy * j)) / self.dy
                z1 = self.grid[(i, j)][2]
                z2 = self.grid[(i + 1, j)][2]
                z3 = self.grid[(i, j + 1)][2]
                z4 = self.grid[(i + 1, j + 1)][2]
                z12 = (1.0 - kx) * z1 + kx * z2
                z34 = (1.0 - kx) * z3 + kx * z4
                Z = (1.0 - ky) * z12 + ky * z34
                # Cut out too big z values
                if last_z < Z:
                    #print 'last_z: ', last_z, ' < Z: ', Z, ' dz: ', Z - last_z
                    Z = last_z
                last_z = Z 
                self.rivers_data_3d[river_id].append( (rp[0], rp[1], Z) )

    def display_terrain(self):
        """
        Try to display terrain
        """

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        plt.hold(True)

        if self.tW is not None:
            terrain_points = ax.scatter(self.tX, self.tY, self.tZ, c=self.tW)
            fig.colorbar(terrain_points, shrink=0.5, aspect=5)
        else:
            terrain_points = ax.scatter(self.tX, self.tY, self.tZ)

        # Draw rivers
        for river_id,river in self.rivers_data_3d.items():
            rx = [item[0] for item in river]
            ry = [item[1] for item in river]
            rz = [item[2] for item in river]
            ax.plot(rx, ry, rz, label=str(river_id))

        # Draw borders
        for border_id,border in self.area_borders_3d.items():
            bx = [item[0] for item in border]
            by = [item[1] for item in border]
            bz = [item[2] for item in border]
            # Make sure border is displayed as cyclic polyline
            bx.append(bx[0])
            by.append(by[0])
            bz.append(bz[0])
            ax.plot(bx, by, bz)

        # Draw bspline patches
        for limit,tck in self.tck.items():
            min_x = limit[0]
            min_y = limit[1]
            max_x = limit[2]
            max_y = limit[3]
            XB = np.arange(min_x, max_x + self.dx / 2.0, self.dx)
            YB = np.arange(min_y, max_y + self.dy / 2.0, self.dy)
            XG,YG = np.meshgrid(XB, YB)
            ZB = interpolate.bisplev(XB, YB, tck)
            surf = ax.plot_surface(XG.transpose(), YG.transpose(), ZB, color='gray', shade=True, alpha=0.5, antialiased=False, rstride=1, cstride=1)
            surf.set_linewidth(0)

        plt.show()

def main(yaml_conf_filename):
    """
    Try to read data from all files
    """
    terrain_data = TerrainData(yaml_conf_filename)

    terrain_data.load_conf_from_yaml()
    terrain_data.load_terrain()
    terrain_data.load_rivers()
    terrain_data.load_area()

    terrain_data.aproximate_terrain()
    terrain_data.aproximate_2d_borders()
    terrain_data.aproximate_2d_rivers()
    
    terrain_data.display_terrain()

if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="Yaml conf file", default=None)
    args = parser.parse_args()
    main(args.filename)
