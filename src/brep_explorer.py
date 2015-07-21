from OCC.Display.SimpleGui import init_display
from OCC.BRepTools import breptools_Read
from OCC.TopoDS import TopoDS_Shape
from OCC.BRep import BRep_Builder

from OCC.TopExp import TopExp_Explorer

from OCC.TopAbs import TopAbs_COMPOUND
from OCC.TopAbs import TopAbs_COMPSOLID
from OCC.TopAbs import TopAbs_SOLID
from OCC.TopAbs import TopAbs_SHELL
from OCC.TopAbs import TopAbs_FACE
from OCC.TopAbs import TopAbs_WIRE
from OCC.TopAbs import TopAbs_EDGE
from OCC.TopAbs import TopAbs_VERTEX
from OCC.TopAbs import TopAbs_SHAPE

import argparse

SHAPE_NAMES = {
    0: 'COMPOUND',
    1: 'COMPSOLID',
    2: 'SOLID',
    3: 'SHELL',
    4: 'FACE',
    5: 'WIRE',
    6: 'EDGE',
    7: 'VERTEX',
    8: 'SHAPE'
}


def get_shape_list(shape, shape_class):
    """
    Return sequence of entities in shape
    """
    explorer = TopExp_Explorer(shape, shape_class)
    sequence = []
    while explorer.More():
        entity = explorer.Current()
        sequence.append(entity)
        explorer.Next()
    return sequence


def print_shape_content(shape, indent=0):
    """
    Print content of shape
    """

    SHAPE_CLASSES = {
        0: ( # TopAbs_COMPOUND 
            TopAbs_COMPSOLID,
            TopAbs_SOLID,
            TopAbs_SHELL,
            TopAbs_FACE,
            TopAbs_WIRE,
            TopAbs_EDGE,
            TopAbs_VERTEX,
            TopAbs_SHAPE
            ),
        1: (TopAbs_SOLID, ),    # CompSolid -> Solid
        2: (TopAbs_SHELL, ),    # Solid -> Shell
        3: (TopAbs_FACE, ),     # Shell - > Face
        4: (TopAbs_WIRE, ),     # Face -> Wire
        5: (TopAbs_EDGE, ),     # Wire -> Edge
        6: (TopAbs_VERTEX, ),   # Edge -> Vertex
        7: (TopAbs_SHAPE, ),    # Vertex -> Shape
        8: ()     # Shape
    }

    shape_type = shape.ShapeType()

    #if shape.Checked() is True:
    #    return

    print indent * " ", SHAPE_NAMES[shape_type], shape
    # shape.Checked(True)

    for sub_shape_type in SHAPE_CLASSES[shape_type]:
        shape_sequence = get_shape_list(shape, sub_shape_type)
        for sub_shape in shape_sequence:
            print_shape_content(sub_shape, indent + 1)
        if len(shape_sequence) != 0:
            break


def main(filename, display_shape=False):
    """
    Main function of this module
    """
    shape = TopoDS_Shape()
    builder = BRep_Builder()
    breptools_Read(shape, filename, builder)

    print_shape_content(shape)


if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="BREP file for exploring", default=None)
    args = parser.parse_args()
    main(args.filename)
