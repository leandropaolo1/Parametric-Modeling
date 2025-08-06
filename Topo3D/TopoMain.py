import Part

import FreeCAD as App

doc = App.ActiveDocument
if doc is None:
    doc = App.newDocument("AutoDoc")


box = App.ActiveDocument.addObject("Part::Box", "BoxFromScript")
box.Length = 30
box.Width = 50
box.Height = 25
App.ActiveDocument.recompute()
print("RUN")