"""
This module allows to create surface form bspline patches and mesh them using
GMSH.
"""


from OCC.gp import *
from OCC.Geom import *
from OCC.TColGeom import *
from OCC.TColgp import * 
from OCC.GeomConvert import *
from OCC.BRepBuilderAPI import *
from OCC.TopoDS import *
from OCC.STEPControl import *
from OCC.Display.SimpleGui import init_display
from OCC.BRepTools import breptools_Write
from OCC.BRepAlgoAPI import *

import argparse

display, start_display, add_menu, add_function_to_menu = init_display()


def add_point_to_array(array, co, point, display_point=False):
    """
    This function creates OCC point (gp_Pnt) from tuple of 3D
    coordinates and this OCC points is added then to the OCC 2D
    array of points.
    """
    gp_point = gp_Pnt(point[0], point[1], point[2])
    if display_point is True:
        display.DisplayShape(gp_point, update=False)
    array.SetValue(co[0], co[1], gp_point)    


def max_indexes(keys):
    """
    Try to find the biggest i and j indexes in the list of tuples.
    Each tuple contains two indexes.
    """
    max_id_i = 0
    max_id_j = 0
    for key in keys:
        if key[0] > max_id_i:
            max_id_i = key[0]
        if key[1] > max_id_j:
            max_id_j = key[1]
    return max_id_i, max_id_j


def create_bspline_surfaces(patches):
    """
    This function creates object representing bspline patches
    """

    # Create OCC 'array' of Bezier surfaces
    max_patch_i, max_patch_j = max_indexes( patches.keys() )
    bezierarray = TColGeom_Array2OfBezierSurface(1, max_patch_i, 1, max_patch_j)

    for patch_id, patch in patches.items():
        # Create OCC 'array' of control points
        max_point_i, max_point_j = max_indexes( patch.keys() )
        array = TColgp_Array2OfPnt(1, max_point_i, 1, max_point_j)
        # Fill this 'array' of control points with coordinates 
        for coord_id, coord3d in patch.items():
            add_point_to_array(array, coord_id, coord3d, True)
        # Create Bezier surface
        bezier_surface = Geom_BezierSurface(array)
        # Add this Bezier surface to 'array' of Bezier surfaces
        bezierarray.SetValue(patch_id[0], patch_id[1], bezier_surface.GetHandle())

    # Create OCC representation of bspline surface from array
    BB = GeomConvert_CompBezierSurfacesToBSplineSurface(bezierarray)

    if BB.IsDone():
        poles = BB.Poles().GetObject().Array2()
        uknots = BB.UKnots().GetObject().Array1()
        vknots = BB.VKnots().GetObject().Array1()
        umult = BB.UMultiplicities().GetObject().Array1()
        vmult = BB.VMultiplicities().GetObject().Array1()
        udeg = BB.UDegree()
        vdeg = BB.VDegree()

        bspline_surface = Geom_BSplineSurface(poles, uknots, vknots, umult, vmult, udeg, vdeg, 0, 0)

    return bspline_surface


def draw_bspline_surface(bspline_surface):
    """
    This function tries to draw bspline surface
    """
    display.DisplayShape(bspline_surface.GetHandle(), update=True)
    start_display()

def main(file_name=None):
    """
    Main function for testing
    """

    # Definition of Bezier patches using indexes and coordinates of control points
    patch1 = {
        (1, 1): (1.0, 1.0, 0.0), (1, 2): (2.0, 1.0, 0.0), (1, 3): (3.0, 1.0, 0.0),
        (2, 1): (1.0, 2.0, 0.0), (2, 2): (2.0, 2.0, 0.0), (2, 3): (3.0, 2.0, 0.0),
        (3, 1): (1.0, 3.0, 0.0), (3, 2): (2.0, 3.0, 0.0), (3, 3): (3.0, 3.0, 0.0)
    }
    patch2 = {
        (1, 1): (3.0, 1.0, 0.0), (1, 2): (4.0, 1.0, 0.0), (1, 3): (5.0, 1.0, 0.0),
        (2, 1): (3.0, 2.0, 0.0), (2, 2): (4.0, 2.0, 0.0), (2, 3): (5.0, 2.0, 0.0),
        (3, 1): (3.0, 3.0, 0.0), (3, 2): (4.0, 3.0, 0.0), (3, 3): (5.0, 3.0, 0.0)
    }
    patch3 = {
        (1, 1): (1.0, 3.0, 0.0), (1, 2): (2.0, 3.0, 0.0), (1, 3): (3.0, 3.0, 0.0),
        (2, 1): (1.0, 4.0, 0.0), (2, 2): (2.0, 4.0, 0.0), (2, 3): (3.0, 4.0, 0.0),
        (3, 1): (1.0, 5.0, 1.0), (3, 2): (2.0, 5.0, 1.0), (3, 3): (3.0, 5.0, 0.0)
    }
    patch4 = {
        (1, 1): (3.0, 3.0, 0.0), (1, 2): (4.0, 3.0, 0.0), (1, 3): (5.0, 3.0, 0.0),
        (2, 1): (3.0, 4.0, 0.0), (2, 2): (4.0, 4.0, 0.0), (2, 3): (5.0, 4.0, 0.0),
        (3, 1): (3.0, 5.0, 0.0), (3, 2): (4.0, 5.0, 1.0), (3, 3): (5.0, 5.0, 1.0)
    }
    patches = {}
    patches[(1, 1)] = patch1
    patches[(1, 2)] = patch2
    patches[(2, 1)] = patch3
    patches[(2, 2)] = patch4

    bspline_surface = create_bspline_surfaces(patches)

    error = 1e-6

    tmp1_patches = {}
    tmp1_patches[(1,1)] = patch1
    tmp1_bs = create_bspline_surfaces(tmp1_patches)
    tmp1_face = BRepBuilderAPI_MakeFace(tmp1_bs.GetHandle(), error).Shape()

    tmp2_patches = {}
    tmp2_patches[(1,1)] = patch2
    tmp2_bs = create_bspline_surfaces(tmp2_patches)
    tmp2_face = BRepBuilderAPI_MakeFace(tmp2_bs.GetHandle(), error).Shape()

    border_curve = BRepAlgoAPI_Common(tmp1_face, tmp2_face).Shape()

    face = BRepBuilderAPI_MakeFace(bspline_surface.GetHandle(), error).Shape()

    mold = BRepAlgoAPI_Fuse(face, border_curve).Shape()

    breptools_Write(mold, file_name)

    draw_bspline_surface(bspline_surface)


if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="Write B-Spline surface to BREP file format", default=None)
    args = parser.parse_args()
    main(args.filename)
