#!/usr/bin/env python

"""
This script tries to print IDs of shapes in brep file.
"""

# print will behave like function in 2.x python too
from __future__ import print_function

import argparse


class Shape(object):
    """docstring for Shape"""
    def __init__(self, shape_id):
        super(Shape, self).__init__()
        self.shape_id = shape_id
        self.items = []
    def __str__(self):
        if self.items != []:
            return '{0}: {1} -> {2}'.format(self.__class__.__name__, self.shape_id, self.items)
        else:
            return '{0}: {1}'.format(self.__class__.__name__, self.shape_id)


def class_factory(name, underlings=None):
    """
    Function used for creating subclasses of class Shape
    """
    def __init__(self, shape_id):
        super(self.__class__, self).__init__(shape_id)
        self.underlings = underlings
    return type(name, (Shape,), {"__init__": __init__})


# Create some classes
Vertex = class_factory('Vertex')
Edge = class_factory('Edge', (Vertex,))
Wire = class_factory('Wire', (Edge,))
Face = class_factory('Face', (Wire,))
Shell = class_factory('Shell', (Face,))
Solid = class_factory('Solid', (Shell,))
CompSolid = class_factory('CompSolid', (Solid,))
Compound = class_factory('Compound', (CompSolid, Solid, Shell, Face, Wire, Edge, Vertex))


def main(filename):
    """
    Main function for processing brep file
    """

    item_disp = {
        'Ve': lambda shape_id: Vertex(shape_id),
        'Ed': lambda shape_id: Edge(shape_id),
        'Wi': lambda shape_id: Wire(shape_id),
        'Fa': lambda shape_id: Face(shape_id),
        'Sh': lambda shape_id: Shell(shape_id),
        'So': lambda shape_id: Solid(shape_id),
        'CS': lambda shape_id: CompSolshape_id(shape_id),
        'Co': lambda shape_id: Compound(shape_id),
    }

    shapes = {
        Vertex: {},
        Edge: {},
        Wire: {},
        Face: {},
        Shell: {},
        Solid: {},
        CompSolid: {},
        Compound: {}
    }

    num_of_items = None
    shape = None

    with open(filename, "r") as brep_file:
        for line in brep_file:
            items = line.split()

            if len(items) > 0:
                if items[0] == 'TShapes':
                    shape_id = num_of_items = int(items[1])
                    print('Number of TShapes:', num_of_items)
                elif items[-1] == '*' and shape is not None:
                    shape.items = [int(item) for idx,item in enumerate(items) if idx % 2 == 0 and item != '*']
                    # Debug print
                    print(shape)
                elif num_of_items is not None and items[0] in item_disp:
                    # Create new shape object
                    shape = item_disp[items[0]](shape_id)
                    # Add shape object to dictionary of shapes
                    shapes[type(shape)][shape_id] = shape
                    shape_id -= 1
            # print(line.rstrip())

    # Print shapes statistics
    print('\nStatistics:')
    for shape_subclass, item in shapes.items():
        print("{0}: {1}".format(shape_subclass.__name__, len(item)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="Modify BREP file", default=None)
    args = parser.parse_args()
    if args.filename is not None:
        main(args.filename)