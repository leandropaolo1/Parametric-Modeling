import ProfileLib.RegularPolygon
import DraftTools
import Sketcher
import FreeCAD as App
import Draft
import math
import Part
import GuiDocument
import FreeCADGui as Gui
hexSeparation = .2
hexExtrusion = 5
hexRadius = 2

"""
Angle with X-axis: 90.0
Angle with Y-axis: 90.0
Angle with Z-axis: 0.0

Angle with X-axis: 90.0
Angle with Y-axis: 90.0
Angle with Z-axis: 0.0
"""


def createSpreadSheet(
        hexRadius: float,
        hexSeparation: float,
        hexExtrusion: float,
        offset2DBoundBox,
        maxOffsetWidth: float,
        maxOffsetLength: float,
        offset2DZPos: float):

    # Create spreadsheet
    worksheet = App.ActiveDocument.addObject("Spreadsheet::Sheet", "EditMe")
    worksheet.setColumnWidth('A', 30)
    set_val = worksheet.set

    # Define aliases for easier reference in expressions
    aliases = {
        'radius':     'B2',
        'separation': 'B3',
        'width':      'B4',
        'length':     'B5',
        'height':     'B6',
        'tweakX':     'B8',
        'tweakY':     'B9',
        'tweakZ':     'B10',
        'xInterval':  'E2',
        'yInterval':  'E3',
        'firstX':     'E4',
        'firstY':     'E5',
        'countX':     'E6',
        'countY':     'E7',
        'array2XPos': 'E8',
        'array2YPos': 'E9',
    }

    for key, cell in aliases.items():
        worksheet.setAlias(cell, key)

    # User variables section
    set_val('A1', 'User Variables')
    set_val('A2', 'Hexagon Radius:')
    set_val(aliases['radius'], str(hexRadius))

    set_val('A3', 'Hexagon Separation:')
    set_val(aliases['separation'], str(hexSeparation))

    set_val('A4', 'Grid Width:')
    set_val(aliases['width'], str(maxOffsetWidth))

    set_val('A5', 'Grid Length:')
    set_val(aliases['length'], str(maxOffsetLength))

    set_val('A6', 'Grid Height:')
    set_val(aliases['height'], str(hexExtrusion))

    set_val('A8', 'Tweak X:')
    set_val(aliases['tweakX'], str(offset2DBoundBox.XMin))

    set_val('A9', 'Tweak Y:')
    set_val(aliases['tweakY'], str(offset2DBoundBox.YMin))

    set_val('A10', 'Tweak Z:')
    set_val(aliases['tweakZ'], str(offset2DZPos))

    # Calculated values section
    set_val('D1', 'Calculated Values')

    set_val('D2', 'X Interval:')
    set_val(aliases['xInterval'], '=2*sin(60deg)*(B2*2+(B3-0.267949*B2))')

    set_val('D3', 'Y Interval:')
    set_val(aliases['yInterval'], '=2*B2+(B3-0.267949*B2)')

    set_val('D4', 'First X:')
    set_val(aliases['firstX'], '=B2')

    set_val('D5', 'First Y:')
    set_val(aliases['firstY'], '=B2')

    set_val('D6', 'Count X:')
    set_val(aliases['countX'], '=round((B5) / E2) + 2')

    set_val('D7', 'Count Y:')
    set_val(aliases['countY'], '=round((B4) / E3) + 2')

    set_val('D8', 'Array2 XPos:')
    set_val(aliases['array2XPos'], '=sin(60deg)*(B2*2+B3-0.2679489*B2)')

    set_val('D9', 'Array2 YPos:')
    set_val(aliases['array2YPos'], '=E3/2')

    return worksheet

def createShapeBinder():
    selected_items = Gui.Selection.getSelectionEx()
    if not selected_items or not selected_items[0].SubObjects:
        raise Exception("Error: Select a face to create the honeycomb grid on.")


    selected_item = selected_items[0]
    doc = App.ActiveDocument
    body = doc.getObject('Body')
    subShapeBinder = body.newObject('PartDesign::SubShapeBinder', 'Binder')
    subShapeBinder.Support = [
        (selected_item.Object, selected_item.SubElementNames[0])]
    doc.recompute()
    subShapeBinder.ViewObject.Visibility = True
    
    return subShapeBinder


def createOffset2D(subShapeBinder):
    offset2D = App.activeDocument().addObject('Part::Offset2D', 'Offset2D')
    offset2D.Source = subShapeBinder
    offset2D.Value = -3
    App.activeDocument().recompute()
    return offset2D

def extrudeShape(shape, length):
    extruded = App.ActiveDocument.addObject('Part::Extrusion', 'Extruded')
    extruded.Base = shape
    extruded.DirMode = "Normal"
    extruded.LengthFwd = length if length > 0 else 0
    extruded.LengthRev = -length if length < 0 else 0
    extruded.Solid = True
    App.ActiveDocument.recompute()
    return extruded

def alignShapeFace(obj1, faceIndex1, obj2, faceIndex2):
    face1 = obj1.Shape.Faces[faceIndex1]
    face2 = obj2.Shape.Faces[faceIndex2]
    
    normal1 = face1.normalAt(0.5, 0.5)
    normal2 = face2.normalAt(0.5, 0.5)
    rotation_axis = normal1.cross(normal2)
    if rotation_axis.Length == 0:
        rotation_axis = App.Vector(1, 0, 0)
    rotation_angle = normal1.getAngle(normal2)
    rotation = App.Rotation(rotation_axis, math.degrees(rotation_angle))
    obj1.Placement.Rotation = rotation.multiply(obj1.Placement.Rotation)
    App.ActiveDocument.recompute()
    
    center1 = face1.CenterOfMass
    center2 = face2.CenterOfMass
    translation = center2 - center1
    obj1.Placement.Base += translation
    App.ActiveDocument.recompute()

def alignShapes(fusedArrays, extrudedOffset):
    alignShapeFace(fusedArrays, 7, extrudedOffset, 0)

        
def createShapeArray(
        offset2DZPos: float,
        selMidPoint: float,
        xInterval: float,
        yInterval: float,
        countX: int,
        countY: int,
        hexRadius: float,
        hexSeparation: float,
        hexExtrusion: float,
        spreadsheetName: str,
        group=None):

    # Create hexagon
    honeycombHexagon = App.ActiveDocument.addObject(
        "Part::RegularPolygon", "HoneycombHexagon")
    if group:
        group.addObject(honeycombHexagon)
    honeycombHexagon.Polygon = 6
    honeycombHexagon.setExpression('Circumradius', f"{spreadsheetName}.radius")
    honeycombHexagon.Visibility = False

    # Create extrusion of hexagon
    extrudedHexagonObject = App.ActiveDocument.addObject(
        'Part::Extrusion', 'ExtrudedHexagon')
    if group:
        group.addObject(extrudedHexagonObject)
    extrudedHexagonObject.Base = honeycombHexagon
    extrudedHexagonObject.setExpression('LengthFwd', f"{spreadsheetName}.height")
    extrudedHexagonObject.Solid = True
    extrudedHexagonObject.setExpression('Placement.Base.x', f"{spreadsheetName}.tweakX")
    extrudedHexagonObject.setExpression('Placement.Base.y', f"{spreadsheetName}.tweakY")

    # Create the two orthogonal arrays
    xvector = App.Vector(xInterval, 0, 0)
    yvector = App.Vector(0, yInterval, 0)

    row1Array = Draft.make_ortho_array(
        extrudedHexagonObject,
        v_x=xvector, v_y=yvector,
        n_x=countX, n_y=countY,
        use_link=False)

    row2Array = Draft.make_ortho_array(
        extrudedHexagonObject,
        v_x=xvector, v_y=yvector,
        n_x=countX, n_y=countY,
        use_link=False)

    App.ActiveDocument.recompute()

    # Position arrays
    row1Array.Placement.Base.z = offset2DZPos
    row2Array.Placement = App.Placement(
        App.Vector(
            math.sin(math.radians(60)) * (hexRadius * 2 + (hexSeparation - 0.267949)),
            yInterval,
            offset2DZPos),
        App.Rotation(0, 0, 0),
        App.Vector(0, 0, 0))

    # Link expressions to spreadsheet
    row2Array.setExpression('Placement.Base.x', f"{spreadsheetName}.array2XPos")
    row2Array.setExpression('Placement.Base.y', f"{spreadsheetName}.array2YPos")

    for arr in (row1Array, row2Array):
        arr.setExpression('IntervalX.x', f"{spreadsheetName}.xInterval")
        arr.setExpression('IntervalY.y', f"{spreadsheetName}.yInterval")
        arr.setExpression('NumberX', f"{spreadsheetName}.countX")
        arr.setExpression('NumberY', f"{spreadsheetName}.countY")

    # Set colors
    row1Array.ViewObject.ShapeColor = (255, 16, 240)  # pink
    row2Array.ViewObject.ShapeColor = (191, 255, 0)   # lime

    # Fuse arrays
    fusedArrys = App.ActiveDocument.addObject("Part::MultiFuse", "Fused_Arrays")
    fusedArrys.Shapes = [row1Array, row2Array]
    if group:
        group.addObject(fusedArrys)

    row1Array.Visibility = False
    row2Array.Visibility = False

    App.ActiveDocument.recompute()
    Gui.SendMsgToActiveView("ViewFit")

    # Center fused arrays on selected face
    arraysMidPoint = fusedArrys.Shape.BoundBox.Center
    fusedArrys.Placement.Base = App.Vector(
        selMidPoint.x - arraysMidPoint.x,
        selMidPoint.y - arraysMidPoint.y)

    Gui.SendMsgToActiveView("ViewFit")

    # Remove the original hexagon sketch to clean up tree
    App.ActiveDocument.removeObject(honeycombHexagon.Name)
    App.ActiveDocument.recompute()

    return fusedArrys

def main():
    # Creates Folder/Group to hold all generated objects
    honeycombGroup = App.ActiveDocument.addObject('App::DocumentObjectGroup', 'HoneycombGrid')

    # Creates Shape Binder from selected face
    subShapeBinder = createShapeBinder()
    honeycombGroup.addObject(subShapeBinder)

    # Create 2D offset of the binder
    offset2D = createOffset2D(subShapeBinder)
    honeycombGroup.addObject(offset2D)

    # Get bounding box of offset shape
    offset2DBoundBox = offset2D.Shape.BoundBox

    # Calculate distances
    maxOffsetLength = offset2DBoundBox.XMax - offset2DBoundBox.XMin
    maxOffsetWidth = offset2DBoundBox.YMax - offset2DBoundBox.YMin

    # Center point & z position
    selMidPoint = offset2DBoundBox.Center
    offset2DZPos = offset2DBoundBox.ZMin

    # Create spreadsheet for parametric control
    worksheet = createSpreadSheet(
        hexRadius,
        hexSeparation,
        hexExtrusion,
        offset2DBoundBox,
        maxOffsetWidth,
        maxOffsetLength,
        offset2DZPos
    )
    spreadsheetName = worksheet.Name
    honeycombGroup.addObject(worksheet)

    # Calculate hex spacing & counts
    xInterval = 2 * math.sin(math.radians(60)) * (hexRadius * 2 + (hexSeparation - 0.267949))
    yInterval = 2 * hexRadius + (hexSeparation - 0.267949)
    countY = int(maxOffsetLength / yInterval)
    countX = int(maxOffsetWidth / xInterval)

    # Extrude the offset shape (base solid)
    extrusion = extrudeShape(offset2D, hexExtrusion)
    honeycombGroup.addObject(extrusion)

    # Create honeycomb array
    fusedArrays = createShapeArray(
        offset2DZPos,
        selMidPoint,
        xInterval,
        yInterval,
        countX,
        countY,
        hexRadius,
        hexSeparation,
        hexExtrusion,
        spreadsheetName=spreadsheetName,
        group=honeycombGroup
    )

    # Optional: align to face (disabled by default)
    # alignShapeFace(fusedArrays, 7, offset2D, 0)

    App.ActiveDocument.recompute()
    Gui.SendMsgToActiveView("ViewFit")


# Only run main if this script is executed directly in FreeCAD
if __name__ == "__main__":
    main()