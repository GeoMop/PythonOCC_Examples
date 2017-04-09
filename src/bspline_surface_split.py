"""
Experiments with splitting
"""

from OCC.BRep import BRep_Tool_Surface
from OCC.BRepAlgoAPI import BRepAlgoAPI_Section, BRepAlgoAPI_Fuse
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, \
    BRepBuilderAPI_GTransform
from OCC.BRepFeat import BRepFeat_MakePrism, BRepFeat_MakeDPrism, BRepFeat_SplitShape, \
    BRepFeat_MakeLinearForm, BRepFeat_MakeRevol
from OCC.BRepLib import breplib_BuildCurves3d
from OCC.BRepOffset import BRepOffset_Skin
from OCC.BRepOffsetAPI import BRepOffsetAPI_MakeThickSolid, BRepOffsetAPI_MakeOffsetShape
from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCC.Display.SimpleGui import init_display
from OCC.GCE2d import GCE2d_MakeLine
from OCC.Geom import Handle_Geom_Plane_DownCast, Geom_Plane
from OCC.Geom2d import Geom2d_Circle
from OCC.GeomAbs import GeomAbs_Arc
from OCC.TopTools import TopTools_ListOfShape
from OCC.TopoDS import TopoDS_Face
from OCC.gp import gp_Pnt2d, gp_Circ2d, gp_Ax2d, gp_Dir2d, gp_Pnt, gp_Pln, gp_Vec, gp_OX, gp_Trsf, gp_GTrsf
from core_topology_traverse import Topo
from OCC.BRepTools import breptools_Write

def split_shape(event=None):
    """
    Example of spliting shape
    """
    display, start_display, add_menu, add_function_to_menu = init_display()

    S = BRepPrimAPI_MakeBox(gp_Pnt(-100, -60, -80), 150, 200, 170).Shape()
    asect = BRepAlgoAPI_Section(S, gp_Pln(1, 2, 1, -15), False)
    asect.ComputePCurveOn1(True)
    asect.Approximation(True)
    asect.Build()
    R = asect.Shape()

    asplit = BRepFeat_SplitShape(S)

    wire1 = BRepBuilderAPI_MakeWire()

    i = 0
    for edg in Topo(R).edges():
        print(edg)
        face = TopoDS_Face()
        if asect.HasAncestorFaceOn1(edg, face):
            print('Adding edge on face and wire: ', face, i)
            asplit.Add(edg, face)
            # Add edge to wire
            if i > 0:
                wire1.Add(edg)
        i += 1
    asplit.Build()
    wire1.Build()

    display.EraseAll()
    display.DisplayShape(asplit.Shape())
    display.DisplayShape(wire1.Shape(), color='blue')
    # display.FitAll()

    start_display()

    breptools_Write(asplit.Shape(), "split1.brep")

def main():
    """
    Main functions
    """
    split_shape()

if __name__ == '__main__':
    main()