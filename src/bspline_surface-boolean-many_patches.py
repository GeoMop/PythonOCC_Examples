"""
Example with boolean operation
"""

from OCC.gp import *
from OCC.Geom import *
from OCC.TColGeom import *
from OCC.TColgp import * 
from OCC.GeomConvert import *
from OCC.BRepBuilderAPI import *
from OCC.TopoDS import *
from OCC.STEPControl import *
from OCC.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Display.SimpleGui import init_display
from OCC.TopTools import TopTools_ListIteratorOfListOfShape
from OCC.BRepTools import breptools_Write
import argparse

display, start_display, add_menu, add_function_to_menu = init_display()


def create_bspline_surface(array):
    """
    Create B-Spline surface from control points of Bezier surface
    """
    bspline_surface = None
    bezier_surface = Geom_BezierSurface(array)
    bezier_array = TColGeom_Array2OfBezierSurface(1, 1, 1, 1)
    bezier_array.SetValue(1, 1, bezier_surface.GetHandle())
    temp = GeomConvert_CompBezierSurfacesToBSplineSurface(bezier_array)
    if temp.IsDone():
        poles = temp.Poles().GetObject().Array2()
        uknots = temp.UKnots().GetObject().Array1()
        vknots = temp.VKnots().GetObject().Array1()
        umult = temp.UMultiplicities().GetObject().Array1()
        vmult = temp.VMultiplicities().GetObject().Array1()
        udeg = temp.UDegree()
        vdeg = temp.VDegree()
        bspline_surface = Geom_BSplineSurface( poles, uknots, vknots, umult, vmult, udeg, vdeg, 0, 0 )
    return bspline_surface


def make_sewing_of_bspline_surfs(list_of_bspline_surfs):
    """
    Create sewing from list of bspline surfaces
    """
    sewing = BRepBuilderAPI_Sewing(0.01, True, True, True, False)
    sewing.SetFloatingEdgesMode(True)
    error = 1e-6
    for bspline_surf in list_of_bspline_surfs:
        face = BRepBuilderAPI_MakeFace(bspline_surf.GetHandle(), error).Shape()
        sewing.Add(face)
    sewing.Perform()
    return sewing


def generate_list_of_bsplines(coo_range, num_x, num_y):
    """
    """
    list_of_bspline_surfs = []

    diff_x = float(coo_range[1][0] - coo_range[0][0]) / num_x
    diff_y = float(coo_range[1][1] - coo_range[0][1]) / num_y

    coo_x = coo_range[0][0]

    print(diff_x, diff_y, coo_x, coo_range[1][0], coo_range[1][1])

    while coo_x < coo_range[1][0]:
        coo_y = coo_range[0][1]    
        while coo_y < coo_range[1][1]:
            array = TColgp_Array2OfPnt(1, 2, 1, 2)
            array.SetValue(1, 1, gp_Pnt(coo_x, coo_y, 0.0))
            array.SetValue(1, 2, gp_Pnt(coo_x + diff_x, coo_y, 0.0))
            array.SetValue(2, 1, gp_Pnt(coo_x, coo_y + diff_y, 0.0))
            array.SetValue(2, 2, gp_Pnt(coo_x + diff_x, coo_y + diff_y, 0.0))

            bspl_surf = create_bspline_surface(array)

            list_of_bspline_surfs.append(bspl_surf)
            coo_y += diff_y
        coo_x += diff_x

    return list_of_bspline_surfs


def fuse_patches(filename=None):
    """
    """
    display.EraseAll()

    coo_range = [[0.0, 0.0], [2.0, 2.0]]
    num_x = 20
    num_y = 20

    list_of_bspline_surfs = generate_list_of_bsplines(coo_range, num_x, num_y)

    # display.DisplayShape(sewing.SewedShape(), update=True)

    array3 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array3.SetValue(1, 1, gp_Pnt(0.25, 0.25, -0.5))
    array3.SetValue(1, 2, gp_Pnt(0.25, 0.25,  0.5))
    array3.SetValue(2, 1, gp_Pnt(1.75, 1.75, -0.5))
    array3.SetValue(2, 2, gp_Pnt(1.75, 1.75,  0.5))

    bspl_surf3 = create_bspline_surface(array3)
    error = 1e-6
    face3 = BRepBuilderAPI_MakeFace(bspl_surf3.GetHandle(), error).Shape()
    # display.DisplayShape(bspl_surf2.GetHandle(), update=True)

    sewing = BRepBuilderAPI_Sewing(0.01, True, True, True, False)
    sewing.SetFloatingEdgesMode(True)

    for bspline_surf in list_of_bspline_surfs:
        face1 = BRepBuilderAPI_MakeFace(bspline_surf.GetHandle(), error).Shape()
        fuse = BRepAlgoAPI_Fuse(face1, face3)
        mold = fuse.Shape()
        sewing.Add(mold)
    sewing.Perform()

    if filename is not None:
        breptools_Write(mold, filename)

    display.DisplayShape(mold, update=True)

    start_display()



def fuse_sewing(filename=None):
    """
    Try to do fuse between sewings and bspline surface
    """
    display.EraseAll()

    coo_range = [[0.0, 0.0], [2.0, 2.0]]
    num_x = 20
    num_y = 20

    list_of_bspline_surfs = generate_list_of_bsplines(coo_range, num_x, num_y)

    print(list_of_bspline_surfs)

    sewing = make_sewing_of_bspline_surfs(list_of_bspline_surfs)

    # display.DisplayShape(sewing.SewedShape(), update=True)

    array3 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array3.SetValue(1, 1, gp_Pnt(0.25, 0.25, -0.5))
    array3.SetValue(1, 2, gp_Pnt(0.25, 0.25,  0.5))
    array3.SetValue(2, 1, gp_Pnt(1.75, 1.75, -0.5))
    array3.SetValue(2, 2, gp_Pnt(1.75, 1.75,  0.5))

    bspl_surf3 = create_bspline_surface(array3)

    # display.DisplayShape(bspl_surf2.GetHandle(), update=True)

    error = 1e-6
    face3 = BRepBuilderAPI_MakeFace(bspl_surf3.GetHandle(), error).Shape()
    fuse = BRepAlgoAPI_Fuse(sewing.SewedShape(), face3)
    mold = fuse.Shape()

    if filename is not None:
        breptools_Write(mold, filename)

    display.DisplayShape(mold, update=True)

    start_display()

if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="Write shape to BREP file format", default=None)
    parser.add_argument("-t", "--type", type=str,
        help="Fuse between sewing/patches", default=None)
    args = parser.parse_args()
    # Display and optionaly output surface to file (IGES file format)
    if args.type in (None, "sewing"):
        fuse_sewing(args.filename)
    elif args.type == "patches":
        fuse_patches(args.filename)
    else:
        print("Wrong type. Not 'sewing' nor 'patches'")
    