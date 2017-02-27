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

# Dictionary of shape names
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

SHAPE_TYPES = { value:key for key,value in SHAPE_NAMES.items() }

# shape.HashCode() requires some magical constant
HASH_CONST = 100000

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


def print_shape_content(shape, base_shape_stats, indent=0):
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

    if shape.Checked() is not True:
        try:
            print indent * " ", SHAPE_NAMES[shape_type], shape.HashCode(HASH_CONST), base_shape_stats[shape_type][shape.HashCode(HASH_CONST)]
        except KeyError:
            print shape_type, "??"
        shape.Checked(True)
    else:
        try:
            print indent * " ", SHAPE_NAMES[shape_type], shape.HashCode(HASH_CONST), base_shape_stats[shape_type][shape.HashCode(HASH_CONST)], " Checked"
        except KeyError:
            print shape_type, "????"

    for sub_shape_type in SHAPE_CLASSES[shape_type]:
        shape_sequence = get_shape_list(shape, sub_shape_type)
        for sub_shape in shape_sequence:
            print_shape_content(sub_shape, base_shape_stats, indent + 1)
        if len(shape_sequence) != 0:
            break


def create_shape_stat(base_shape):
    """
    This function create statistics of shapes count (duplicities)
    """
    SHAPE_TYPES = (
        TopAbs_COMPSOLID,
        TopAbs_SOLID,
        TopAbs_SHELL,
        TopAbs_FACE,
        TopAbs_WIRE,
        TopAbs_EDGE,
        TopAbs_VERTEX,
        TopAbs_SHAPE
    )

    shape_stats = {
        TopAbs_COMPSOLID: {},
        TopAbs_SOLID: {},
        TopAbs_SHELL: {},
        TopAbs_FACE: {},
        TopAbs_WIRE: {},
        TopAbs_EDGE: {},
        TopAbs_VERTEX: {},
        TopAbs_SHAPE: {}
    }

    for shape_type in SHAPE_TYPES:
        explorer = TopExp_Explorer(base_shape, shape_type)
        while explorer.More():
            shape = explorer.Current()
            if shape.HashCode(HASH_CONST) not in shape_stats[shape_type]:
                shape_stats[shape_type][shape.HashCode(HASH_CONST)] = 1
            else:
                shape_stats[shape_type][shape.HashCode(HASH_CONST)] += 1
            explorer.Next()

    return shape_stats


def shape_disassembly(base_shape, shape_primitives=None):
    """
    This function tries to disable shape to list of basic components
    """
    SHAPE_TYPES = (
        TopAbs_COMPSOLID,
        TopAbs_SOLID,
        TopAbs_SHELL,
        TopAbs_FACE,
        TopAbs_WIRE,
        TopAbs_EDGE,
        TopAbs_VERTEX,
        TopAbs_SHAPE
    )

    if shape_primitives is None:
        shape_primitives = {
            TopAbs_COMPSOLID: {},
            TopAbs_SOLID: {},
            TopAbs_SHELL: {},
            TopAbs_FACE: {},
            TopAbs_WIRE: {},
            TopAbs_EDGE: {},
            TopAbs_VERTEX: {},
            TopAbs_SHAPE: {}
        }

    for shape_type in SHAPE_TYPES:
        explorer = TopExp_Explorer(base_shape, shape_type)
        while explorer.More():
            shape = explorer.Current()
            if shape.HashCode(HASH_CONST) not in shape_primitives[shape_type]:
                shape_primitives[shape_type][shape.HashCode(HASH_CONST)] = shape
            explorer.Next()

    return shape_primitives


def shapes_disassembly(base_shapes):
    """
    This function tries to disassembly itterable variable of shapes into list of primitives
    """
    shape_primitives = None
    for shape in base_shapes:
        shape_primitives = shape_disassembly(shape, shape_primitives)
    return shape_primitives


def print_stat(base_shape_stats):
    """
    This function print statistics about shape
    """
    for shape_type,shape_type_stat in base_shape_stats.items():
        counter = 0
        for shape_count in shape_type_stat.values():
            counter += shape_count
        print SHAPE_NAMES[shape_type], ":", len(shape_type_stat), "x", counter


def main(filename, display_shape=False):
    """
    Main function of this module
    """
    base_shape = TopoDS_Shape()
    builder = BRep_Builder()
    breptools_Read(base_shape, filename, builder)

    base_shape_stats = create_shape_stat(base_shape)

    print "Statistics:"
    print_stat(base_shape_stats)
    print ""
    print "Topology:"
    print_shape_content(base_shape, base_shape_stats)


if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="BREP file for exploring", default=None)
    args = parser.parse_args()
    main(args.filename)
