import ProfileLib.RegularPolygon
import DraftTools
import Sketcher
import FreeCAD
import Draft
import math
import Part


hexSeparation = .25
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
        offset2DBoundBox: float,
        maxOffsetWidth: float,
        maxOffsetLength: float,
        offset2DZPos: float):

    worksheet = App.ActiveDocument.addObject("Spreadsheet::Sheet", "EditMe")
    worksheet.setColumnWidth('A', 30)
    set = worksheet.set

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

    for k, v in aliases.items():
        worksheet.setAlias(v, k)

    set('A1', 'User Variables')
    set('D1', 'Calculated Values')
    set('A2', 'Hexagon Radius:')
    set(aliases['radius'], str(hexRadius))
    set('A3', 'Hexagon Separation:')
    set(aliases['separation'], str(hexSeparation))
    set('A4', 'Grid Width:')
    set(aliases['width'], str(maxOffsetWidth))
    set('A5', 'Grid Length:')
    set(aliases['length'], str(maxOffsetLength))
    set('A6', 'Grid Height:')
    set(aliases['height'], str(hexExtrusion))
    set('A8', 'Tweak X:')
    set(aliases['tweakX'], str(offset2DBoundBox.XMin))
    set('A9', 'Tweak Y:')
    set(aliases['tweakY'], str(offset2DBoundBox.YMin))
    set('A10', 'Tweak Z:')
    set(aliases['tweakZ'], str(offset2DZPos))

    set('D2', 'X Interval:')
    set(aliases['xInterval'], '=2*sin(60deg)*(B2*2+(B3-0.267949*B2))')
    set('D3', 'Y Interval:')
    set(aliases['yInterval'], '=2*B2+(B3-0.267949*B2)')
    set('D4', 'First X:')
    set(aliases['firstX'], '=B2')
    set('D5', 'First Y:')
    set(aliases['firstY'], '=B2')
    set('D6', 'Count X:')
    set(aliases['countX'], '=round((B5) / E2) + 2')
    set('D7', 'Count Y:')
    set(aliases['countY'], '=round((B4) / E3) + 2')
    set('D8', 'Array2 XPos:')
    set(aliases['array2XPos'], '=sin(60deg)*(B2*2+B3-0.2679489*B2)')
    set('D9', 'Array2 YPos:')
    set(aliases['array2YPos'], '=E3/2')

    return worksheet


def createShapeBinder():
    selected_items = FreeCADGui.Selection.getSelectionEx()
    if not selected_items or not selected_items[0].SubObjects:
        raise StandardError(
            "Error: Select a face to create the honeycomb grid on.")

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
        hexExtrusion: float):

    honeycombHexagon = App.ActiveDocument.addObject(
        "Part::RegularPolygon", "HoneycombHexagon")
    
    honeycombHexagon.Polygon = 6
    honeycombHexagon.setExpression('Circumradius', 'EditMe.radius')
    honeycombHexagon.Visibility = False


    extrudedHexagonObject = App.ActiveDocument.addObject(
        'Part::Extrusion', 'ExtrudedHexagon')
    extrudedHexagonObject.Base = honeycombHexagon
    extrudedHexagonObject.setExpression('LengthFwd', 'EditMe.height')
    extrudedHexagonObject.Solid = True
    extrudedHexagonObject.setExpression(
        'Placement.Base.x',
        'EditMe.tweakX')

    extrudedHexagonObject.setExpression(
        'Placement.Base.y',
        'EditMe.tweakY')

    xvector = App.Vector(xInterval, 0, 0)
    yvector = App.Vector(0, yInterval, 0)

    row1Array = Draft.make_ortho_array(
        extrudedHexagonObject,
        v_x=xvector,
        v_y=yvector,
        n_x=countX,
        n_y=countY,
        use_link=False)

    row2Array = Draft.make_ortho_array(
        extrudedHexagonObject,
        v_x=xvector,
        v_y=yvector,
        n_x=countX,
        n_y=countY,
        use_link=False)

    App.ActiveDocument.recompute()

    row1Array.Placement.Base.z = offset2DZPos

    row2Array.Placement = App.Placement(
        App.Vector(
            math.sin(60*math.pi/180.0)*(hexRadius*2+(hexSeparation-0.267949)),
            yInterval,
            offset2DZPos),
        App.Rotation(0, 0, 0),
        App.Vector(0, 0, 0))

    row2Array.setExpression('Placement.Base.x', 'EditMe.array2XPos')
    row2Array.setExpression('Placement.Base.y', 'EditMe.array2YPos')

    row1Array.setExpression('IntervalX.x', 'EditMe.xInterval')
    row1Array.setExpression('IntervalY.y', 'EditMe.yInterval')
    row1Array.setExpression('NumberX', 'EditMe.countX')
    row1Array.setExpression('NumberY', 'EditMe.countY')

    row2Array.setExpression('IntervalX.x', 'EditMe.xInterval')
    row2Array.setExpression('IntervalY.y', 'EditMe.yInterval')
    row2Array.setExpression('NumberX', 'EditMe.countX')
    row2Array.setExpression('NumberY', 'EditMe.countY')

    row1Array.ViewObject.ShapeColor = (255, 16, 240)  # pink
    row2Array.ViewObject.ShapeColor = (191, 255, 0)  # lime

    fusedArrys = App.activeDocument().addObject("Part::MultiFuse", "Fused_Arrays")
    fusedArrys.Shapes = [row1Array, row2Array,]
    row1Array.Visibility = False
    row2Array.Visibility = False

    App.ActiveDocument.recompute()
    Gui.SendMsgToActiveView("ViewFit")

    arraysMidPoint = fusedArrys.Shape.BoundBox.Center
    fusedArrys.Placement.Base = App.Vector(
        selMidPoint.x - arraysMidPoint.x,
        selMidPoint.y - arraysMidPoint.y)

    Gui.SendMsgToActiveView("ViewFit")
    App.activeDocument().removeObject("HoneycombHexagon001")
    App.ActiveDocument.recompute()
    return fusedArrys

# Creates Shape Binder
if App.
subShapeBinder = createShapeBinder()

# Create Offset
offset2D = createOffset2D(subShapeBinder)

# Retrives the outline
offset2DBoundBox = offset2D.Shape.BoundBox

# Calculates distance
maxOffsetLength = offset2DBoundBox.XMax - offset2DBoundBox.XMin
maxOffsetWidth = offset2DBoundBox.YMax - offset2DBoundBox.YMin

# Gives you the corners
minSelX = offset2DBoundBox.XMin
minSelY = offset2DBoundBox.YMin

# Gives you the center
selMidPoint = offset2DBoundBox.Center

# Gives you the z coordinate
offset2DZPos = offset2DBoundBox.ZMin

# Creates Spreadsheat
worksheet = createSpreadSheet(
    hexRadius,
    hexSeparation,
    hexExtrusion,
    offset2DBoundBox,
    maxOffsetWidth,
    maxOffsetLength,
    offset2DZPos)


xInterval = 2*math.sin(math.pi/180.0*60)*(hexRadius*2+(hexSeparation-0.267949))
yInterval = 2*hexRadius+(hexSeparation-0.267949)
firstX = hexRadius
firstY = hexRadius

countY = int((maxOffsetLength) / yInterval)
countX = int((maxOffsetWidth) / xInterval)

extrudeShape(offset2D, hexExtrusion)

fusedArrays=createShapeArray(
    offset2DZPos,
    selMidPoint,
    xInterval,
    yInterval,
    countX,
    countY,
    hexRadius,
    hexSeparation,
    hexExtrusion)

#alignShapeFace(fusedArrays, 7, offset2D, 0)
