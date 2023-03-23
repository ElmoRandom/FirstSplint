
import adsk.core, adsk.fusion, adsk.cam, traceback
import math

app = adsk.core.Application.get()
ui = app.userInterface
design = app.activeProduct
handlers = []
selectedEdges = []
defaultMainDiameter = 2.5
defaultMainThickness = 0.3
defaultMainLength = 1.0
defaultConnectLength = 2.0
defaultSubConnectLength = 2.7
defaultJointRadius = 0.27
defaultJointThickness = 0.23
defaultSubDiameter = 2.0
defaultSubLength = 1.0
defaultJointTol = -0.02 
defaultJointRotateTol = 0.07

def createNewComponent():
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    return newOcc.component
def stringVector(vector):
    return "x: {}, y: {}, z: {}".format(vector.x, vector.y, vector.z)
def addPoint(point1, point2):
    return adsk.core.Point3D.create(point1.x + point2.x, point1.y+ point2.y, point1.z + point2.z)
def point(x,y,z):
    return adsk.core.Point3D.create(x,y,z)
def degToRad(deg):
    return math.pi * deg /180
class MyCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs
            splint = Splint()
            for input in inputs:
                if input.id == 'mainDiameter':
                    splint.mainRadius = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'mainThickness':
                    splint.mainThickness = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'mainLength':
                    splint.mainLength = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'connectLength':
                    splint.connectLength = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'subConnectLength':
                    splint.subConnectLength = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'jointRadius':
                    splint.jointRadius = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'jointThickness':
                    splint.jointThickness = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'jointTol':
                    splint.jointTol = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'jointRotateTol':
                    splint.jointRotateTol = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'subDiameter':
                    splint.subRadius = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'subLength':
                    splint.subLength = unitsMgr.evaluateExpression(input.expression, "cm")
            splint.buildP1()
            splint.buildP2()
            splint.assemble()
            args.isValidResult = True
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MyCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False
            onExecute = MyCommandExecuteHandler()
            cmd.execute.add(onExecute)
            executePreview = MyCommandExecuteHandler()
            cmd.executePreview.add(executePreview)
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            handlers.append(onExecute)
            handlers.append(executePreview)
            handlers.append(onDestroy)

            #create inputs
            inputs = cmd.commandInputs
            initMainDiameter = adsk.core.ValueInput.createByReal(defaultMainDiameter)
            inputs.addValueInput('mainDiameter','Main Diameter', 'cm', initMainDiameter)
            initMainThickness = adsk.core.ValueInput.createByReal(defaultMainThickness)
            inputs.addValueInput('mainThickness', 'Main Thickness', 'cm', initMainThickness)
            initMainLength = adsk.core.ValueInput.createByReal(defaultMainLength)
            inputs.addValueInput('mainLength', 'Main Length', 'cm', initMainLength)
            initConnectLength = adsk.core.ValueInput.createByReal(defaultConnectLength)
            inputs.addValueInput('connectLength', 'Connect Length', 'cm', initConnectLength)
            initSubConnectLength = adsk.core.ValueInput.createByReal(defaultSubConnectLength)
            inputs.addValueInput('subConnectLength', 'Sub Connect Length', 'cm', initSubConnectLength)
            initJointRadius = adsk.core.ValueInput.createByReal(defaultJointRadius)
            inputs.addValueInput('jointRadius', 'Joint Radius', 'cm', initJointRadius)
            initJointThickness = adsk.core.ValueInput.createByReal(defaultJointThickness)
            inputs.addValueInput('jointThickness', 'Joint Thickness', 'cm', initJointThickness)
            initJointTol = adsk.core.ValueInput.createByReal(defaultJointTol)
            inputs.addValueInput('jointTol', 'Joint Tolerance', 'cm', initJointTol)
            initJointRotateTol = adsk.core.ValueInput.createByReal(defaultJointRotateTol)
            inputs.addValueInput('jointRotateTol', 'Joint Rotate Tolerance', 'cm', initJointRotateTol)
            initSubDiameter = adsk.core.ValueInput.createByReal(defaultSubDiameter)
            inputs.addValueInput('subDiameter', 'Sub Diameter', 'cm', initSubDiameter)
            initSubLength = adsk.core.ValueInput.createByReal(defaultSubLength)
            inputs.addValueInput('subLength', 'Sub Length', 'cm', initSubLength)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class Splint:
    def __init__(self):
        self._mainRadius = defaultMainDiameter/2
        self._mainThickness = defaultMainThickness
        self._mainLength = defaultMainLength
        self._connectLength = defaultConnectLength 
        self._subConnectLength = defaultSubConnectLength
        self._jointRadius = defaultJointRadius
        self._jointThickness = defaultJointThickness
        self._jointTol = defaultJointTol
        self._jointRotateTol = defaultJointRotateTol 
        self._intersectLength = 0.01
        self._subRadius = defaultSubDiameter/2 
        self._subLength = defaultSubLength 
    @property
    def mainRadius(self):
        return self._mainRadius
    @mainRadius.setter
    def mainRadius(self, value):
        self._mainRadius = value/2

    @property
    def mainThickness(self):
        return self._mainThickness
    @mainThickness.setter
    def mainThickness(self, value):
        self._mainThickness = value

    @property
    def mainLength(self):
        return self._mainLength
    @mainLength.setter
    def mainLength(self, value):
        self._mainLength = value
    
    @property
    def subConnectLength(self):
        return self._subConnectLength
    @subConnectLength.setter
    def subConnectLength(self, value):
        self._subConnectLength = value
    
    @property
    def connectLength(self):
        return self._connectLength
    @connectLength.setter
    def connectLength(self, value):
        self._connectLength = value
    
    @property
    def jointRadius(self):
        return self._jointRadius
    @jointRadius.setter
    def jointRadius(self, value):
        self._jointRadius = value
    
    @property
    def jointThickness(self):
        return self._jointThickness
    @mainLength.setter
    def jointThickness(self, value):
        self._jointThickness = value

    @property
    def jointTol(self):
        return self._jointTol
    @mainLength.setter
    def jointTol(self, value):
        self._jointTol = value

    @property
    def jointRotateTol(self):
        return self._jointRotateTol
    @mainLength.setter
    def jointRotateTol(self, value):
        self._jointRotateTOl = value

    @property
    def subRadius(self):
        return self._subRadius
    @mainLength.setter
    def subRadius(self, value):
        self._subRadius = value/2
    
    @property
    def subLength(self):
        return self._subLength
    @mainLength.setter
    def subLength(self, value):
        self._subLength = value

    def buildP1(self):
        try:
            self.comp1 = createNewComponent()
            if self.comp1 is None:
                ui.messageBox("New Component Failed to Create")

            sketches = self.comp1.sketches
            features = self.comp1.features
            planes = self.comp1.constructionPlanes
            extrudeFeatures = features.extrudeFeatures
            loftFeatures = features.loftFeatures
            yZPlane = self.comp1.yZConstructionPlane
            xYPlane = self.comp1.xYConstructionPlane
            xZPlane = self.comp1.xZConstructionPlane
            center = adsk.core.Point3D.create(0,0,0)
            yZSketch = sketches.add(yZPlane)
            xYSketch = sketches.add(xYPlane)

            yZCircles = yZSketch.sketchCurves.sketchCircles
            innerCircle = yZCircles.addByCenterRadius(center, self._mainRadius)
            outerCircle = yZCircles.addByCenterRadius(center, self._mainRadius + self._mainThickness)
            
            temp = self._mainRadius + self._mainThickness
            if(self._mainThickness <= 0.4):
                temp = self._mainRadius + 0.4

            point1 = adsk.core.Point3D.create(0,temp,0)
            point2 = adsk.core.Point3D.create(0,-temp,0)
            yZSketch.sketchCurves.sketchLines.addByTwoPoints(point1, point2)
            point3 = adsk.core.Point3D.create(0.6,temp,0)
            point4 = adsk.core.Point3D.create(0.6,-temp,0)
            yZSketch.sketchCurves.sketchLines.addByTwoPoints(point1, point3)
            yZSketch.sketchCurves.sketchLines.addByTwoPoints(point2, point4)
            mainLine = yZSketch.sketchCurves.sketchLines.addByTwoPoints(point3, point4)
            extProfs = adsk.core.ObjectCollection.create()
            ui.activeSelections.clear()
            for profile in yZSketch.profiles:
                for profileLoop in profile.profileLoops:
                    check = 0
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity == mainLine :
                            check+=1
                        elif profileCurve.sketchEntity == outerCircle:
                            check+=1
                    if check >= 2:
                        extProfs.add(profile)
            mainLength = adsk.core.ValueInput.createByReal(self._mainLength)
    
            ext1 = extrudeFeatures.addSimple(extProfs,mainLength, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            strapPoint1 = adsk.core.Point3D.create(0.1, 0.1 + self._mainRadius,0)
            strapPoint2 = adsk.core.Point3D.create(self._mainLength-0.1, 0.3 + self._mainRadius, 0)
            xYSketch.sketchCurves.sketchLines.addTwoPointRectangle(strapPoint1, strapPoint2)
            strapHoleEx = adsk.core.ValueInput.createByReal(-self._mainRadius)
            strapProfile = xYSketch.profiles.item(0)
            ext2 = extrudeFeatures.createInput(strapProfile, adsk.fusion.FeatureOperations.CutFeatureOperation)
            ext2.setDistanceExtent(False, strapHoleEx)
            ext2.participantBodies = [ext1.bodies.item(0)]
            ext2Temp = extrudeFeatures.add(ext2)
            
            selectFace = None
            for bRepFace in ext1.sideFaces:
                (boolVal1, normalVector) = bRepFace.evaluator.getNormalAtPoint(bRepFace.centroid)
                normVect = normalVector.copy()
                xZPlanar = xZPlane.geometry
                xZNorm = xZPlanar.normal
                if normVect.isParallelTo(xZNorm) and bRepFace.centroid.y > 0:
                    selectFace = bRepFace
                    break

            sidePlaneInput = planes.createInput()
            sidePlaneInput.setByTangentAtPoint(selectFace, selectFace.centroid)
            sidePlane = planes.add(sidePlaneInput)
            sideSketch = sketches.add(sidePlane)
            sideCircles = sideSketch.sketchCurves.sketchCircles
            jointPoint = adsk.core.Point3D.create(self._connectLength,0.3,0)
            jointInnerRing = sideCircles.addByCenterRadius(jointPoint, self._jointRadius)
            jointOuterRing = sideCircles.addByCenterRadius(jointPoint, self._jointRadius + self._jointThickness)
            points = []
            largeRadius = self._jointRadius + self._jointThickness
            points.append(addPoint(jointPoint,point(0,-largeRadius,0)))
            points.append(addPoint(jointPoint,point(-largeRadius,-largeRadius,0)))
            points.append(addPoint(jointPoint,point(-largeRadius,largeRadius,0)))
            points.append(addPoint(jointPoint,point(0,largeRadius,0)))
            lines = []
            for i in range(3):
                lines.append(sideSketch.sketchCurves.sketchLines.addByTwoPoints(points[i],points[i+1]))

            extProfs = adsk.core.ObjectCollection.create()
            jointProf = None
            for profile in sideSketch.profiles:
                for profileLoop in profile.profileLoops:
                    check = False
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity == jointOuterRing:
                            check = True

                    if check:
                        extProfs.add(profile)
                    else:
                        jointProf = profile
            
            extLength = adsk.core.ValueInput.createByReal(-0.2)
            ext3 = extrudeFeatures.addSimple(extProfs, extLength, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            self._ref1 = jointInnerRing
            planeInput = planes.createInput()
            offsetValue = adsk.core.ValueInput.createByReal(self._mainLength)
            planeInput.setByOffset(yZPlane, offsetValue)
            sketch4Plane = planes.add(planeInput)
            sketch4 = sketches.add(sketch4Plane)
            selectFaceMain = []
            selectFaceMain.append(ext1.endFaces.item(0))
            projectedEntities = sketch4.intersectWithSketchPlane(selectFaceMain)
            largeRadius = self._mainRadius + self._mainThickness + self._intersectLength
            cutLine = sketch4.sketchCurves.sketchLines.addByTwoPoints(center, point(math.cos(degToRad(45))* largeRadius, math.sin(degToRad(45)) * largeRadius,0))

            profSelect = adsk.core.ObjectCollection.create()
            count =0
            for profile in sketch4.profiles:
                for profileLoop in profile.profileLoops:
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity.objectType == sketch4.sketchCurves.sketchLines.item(0).classType():
                            curve = profileCurve.sketchEntity
                            curveVector = curve.worldGeometry.asInfiniteLine().direction
                            zVector = self.comp1.zConstructionAxis.geometry.direction
                            sketchPoint = curve.endSketchPoint.worldGeometry
                            if curveVector.isParallelTo(zVector) and sketchPoint.y > 0 and curve.length == 0.6:
                                profSelect.add(profile)
            count = 0
            profTwo = None
            for bRepFace in ext3.sideFaces:
                (tempBool, normVect) = bRepFace.evaluator.getNormalAtPoint(bRepFace.centroid)
                edges = bRepFace.edges
                passed = 0
                if normVect.isParallelTo(yZPlane.geometry.normal):
                    passed += 1
                for edge in bRepFace.edges:
                    (boolTemp, startPoint, endPoint) = edge.evaluator.getEndPoints()
                    if bRepFace.geometry.surfaceType == 0:
                            passed += 1
                            break                            
                if(passed == 2):
                    count+=1
                    profTwo = bRepFace
            loftInput = loftFeatures.createInput(adsk.fusion.FeatureOperations.JoinFeatureOperation)
            loftObjects = loftInput.loftSections
            loftObjects.add(profSelect)
            loftObjects.add(profTwo)
            loft1 = loftFeatures.add(loftInput)

            points = []
            points.append(adsk.core.Point3D.create(-0.8,-0.885,0))
            points.append(adsk.core.Point3D.create(-0.8,-1.4,0))
            points.append(adsk.core.Point3D.create(-1.3,-1.4,0))
            points.append(adsk.core.Point3D.create(-1.3,-1.3,0))
            points.append(adsk.core.Point3D.create(-0.94, -1.3,0))
            points.append(adsk.core.Point3D.create(-0.94, -1.02,0))
            points.append(adsk.core.Point3D.create(-1.3, -1.02,0))
            points.append(adsk.core.Point3D.create(-1.3,-0.885))
            lines = []
           for i in range(len(points)):
                lines.append(sideSketch.sketchCurves.sketchLines.addByTwoPoints(points[i], points[(i+1)%len(points)]))

            sideSketch.sketchCurves.sketchLines.addByTwoPoints(center, points[1])
            tempCurve = sideSketch.sketchCurves.sketchLines.addByTwoPoints(adsk.core.Point3D.create(0,0.6,0),points[len(points)-1])
            sideSketch.sketchCurves.sketchLines.addByTwoPoints(center, adsk.core.Point3D.create(0,0.6,0))
            cur = None
            for profile in sideSketch.profiles:
                for profileLoop in profile.profileLoops:
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity == tempCurve:
                            cur = profile
            extLength = adsk.core.ValueInput.createByReal(-0.3)
            ext4 = extrudeFeatures.addSimple(cur, extLength, adsk.fusion.FeatureOperations.JoinFeatureOperation)
            cur = None
            for profile in sideSketch.profiles:
                for profileLoop in profile.profileLoops:
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity == lines[4]:
                            cur = profile
            ext5 = extrudeFeatures.addSimple(cur, extLength, adsk.fusion.FeatureOperations.JoinFeatureOperation)

            mirrorFeatures = features.mirrorFeatures
            inputEntities = adsk.core.ObjectCollection.create()
            inputEntities.add(ext2Temp)
            inputEntities.add(ext3)
            inputEntities.add(loft1)
            inputEntities.add(ext4)
            inputEntities.add(ext5)
            mirrorInput = mirrorFeatures.createInput(inputEntities, xZPlane)
            mirrorFeatures.add(mirrorInput)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
    def buildP2(self):
        try:
            self.comp2 = createNewComponent()
            if self.comp2 is None:
                ui.messageBox("New Component Failed to Create")

            sketches = self.comp2.sketches
            features = self.comp2.features
            planes = self.comp2.constructionPlanes
            extrudeFeatures = features.extrudeFeatures
            loftFeatures = features.loftFeatures
            yZPlane = self.comp2.yZConstructionPlane
            xYPlane = self.comp2.xYConstructionPlane
            xZPlane = self.comp2.xZConstructionPlane
            center = adsk.core.Point3D.create(0,0,0)
            yZSketch = sketches.add(yZPlane)
            xYSketch = sketches.add(xYPlane)

            yZCircles = yZSketch.sketchCurves.sketchCircles
            innerCircle = yZCircles.addByCenterRadius(center, self._subRadius)
            outerCircle = yZCircles.addByCenterRadius(center, self._subRadius + self._mainThickness)       
            temp = self._subRadius + self._mainThickness
            if(self._mainThickness <= 0.4):
                temp = self._subRadius + 0.4

            point1 = adsk.core.Point3D.create(0,temp,0)
            point2 = adsk.core.Point3D.create(0,-temp,0)
            yZSketch.sketchCurves.sketchLines.addByTwoPoints(point1, point2)
            point3 = adsk.core.Point3D.create(0.6,temp,0)
            point4 = adsk.core.Point3D.create(0.6,-temp,0)
            yZSketch.sketchCurves.sketchLines.addByTwoPoints(point1, point3)
            yZSketch.sketchCurves.sketchLines.addByTwoPoints(point2, point4)
            mainLine = yZSketch.sketchCurves.sketchLines.addByTwoPoints(point3, point4)
            extProfs = adsk.core.ObjectCollection.create()
            ui.activeSelections.clear()
            for profile in yZSketch.profiles:
                for profileLoop in profile.profileLoops:
                    check = 0
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity == mainLine :
                            check+=1
                        elif profileCurve.sketchEntity == outerCircle:
                            check+=1
                    if check >= 2:
                        extProfs.add(profile)
            mainLength = adsk.core.ValueInput.createByReal(self._subLength) #input parameters here
            ext1 = extrudeFeatures.addSimple(extProfs,mainLength, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            strapPoint1 = adsk.core.Point3D.create(0.1, 0.1 + self._subRadius,0)
            strapPoint2 = adsk.core.Point3D.create(self._subLength-0.1, 0.3 + self._subRadius, 0)
            xYSketch.sketchCurves.sketchLines.addTwoPointRectangle(strapPoint1, strapPoint2)
            strapHoleEx = adsk.core.ValueInput.createByReal(-self._mainRadius)
            strapProfile = xYSketch.profiles.item(0)
            ext2 = extrudeFeatures.createInput(strapProfile, adsk.fusion.FeatureOperations.CutFeatureOperation)
            ext2.setDistanceExtent(False, strapHoleEx)
            ext2.participantBodies = [ext1.bodies.item(0)]
            extrudeFeatures.add(ext2)
            temp = self._mainRadius + self._mainThickness
            if(self._mainThickness <= 0.4):
                temp = self._mainRadius + 0.4
            
            offsetValue = temp - 0.3 - self._jointTol

            planeInput = planes.createInput()
            offsetValue = adsk.core.ValueInput.createByReal(offsetValue)
            planeInput.setByOffset(xZPlane, offsetValue)
            sketch3Plane = planes.add(planeInput)
            sketch3 = sketches.add(sketch3Plane)
            jointPoint = adsk.core.Point3D.create(-self._subConnectLength + self._subLength,0.3,0)
            sideCircles = sketch3.sketchCurves.sketchCircles
            jointInnerRing = sideCircles.addByCenterRadius(jointPoint, self._jointRadius - self._jointRotateTol)
            jointOuterRing = sideCircles.addByCenterRadius(jointPoint, self._jointRadius + self._jointThickness)
            points = []
            largeRadius = self._jointRadius + self._jointThickness
            points.append(addPoint(jointPoint,point(0,-largeRadius,0)))
            points.append(addPoint(jointPoint,point(largeRadius,-largeRadius,0)))
            points.append(addPoint(jointPoint,point(largeRadius,largeRadius,0)))
            points.append(addPoint(jointPoint,point(0,largeRadius,0)))
            lines = []
            for i in range(3):
                lines.append(sketch3.sketchCurves.sketchLines.addByTwoPoints(points[i],points[i+1]))
            
            profs = adsk.core.ObjectCollection.create()
            for profile in sketch3.profiles:
                profs.add(profile)
            
            extLength = adsk.core.ValueInput.createByReal(-0.3)
            ext3 = extrudeFeatures.addSimple(profs, extLength, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extLengthOp = adsk.core.ValueInput.createByReal(0.3 + self._jointTol)

            selectProf = None
            for profile in sketch3.profiles:
                for profileLoop in profile.profileLoops:
                    check = False
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity == jointInnerRing :
                            check = True
                    if check and profileLoop.profileCurves.count == 1 and profile.profileLoops.count == 1:
                        selectProf = profile
            ext4 = extrudeFeatures.addSimple(selectProf, extLengthOp, adsk.fusion.FeatureOperations.JoinFeatureOperation)

            self._ref2 = selectProf            

            sketch4 = sketches.add(yZPlane)
            mainBody = ext1.bodies.item(0)
            selectFaceMain = []
            for bRepFace in mainBody.faces:
                (boolVal1, normalVector) = bRepFace.evaluator.getNormalAtPoint(bRepFace.centroid)
                normVect = normalVector.copy()
                yZPlanar = yZPlane.geometry
                yZNorm = yZPlanar.normal
                if yZNorm.isParallelTo(normVect) and bRepFace.centroid.x == 0.0:
                    selectFaceMain.append(bRepFace)

            projectedEntities = sketch4.intersectWithSketchPlane(selectFaceMain)
            largeRadius = self._subRadius + self._mainThickness + self._intersectLength
            cutLine = sketch4.sketchCurves.sketchLines.addByTwoPoints(center, point(math.cos(degToRad(45))* largeRadius, math.sin(degToRad(45)) * largeRadius,0))
            profSelect = adsk.core.ObjectCollection.create()
            count =0
            for profile in sketch4.profiles:
                for profileLoop in profile.profileLoops:
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity.objectType == sketch4.sketchCurves.sketchLines.item(0).classType():
                            curve = profileCurve.sketchEntity
                            curveVector = curve.worldGeometry.asInfiniteLine().direction
                            zVector = self.comp2.zConstructionAxis.geometry.direction
                            sketchPoint = curve.endSketchPoint.worldGeometry
                            if curveVector.isParallelTo(zVector) and curve.length == 0.6:
                                count+=1
                            if curveVector.isParallelTo(zVector) and sketchPoint.y > 0 and curve.length == 0.6:
                                profSelect.add(profile)

            count = 0
            profTwo = None
            for bRepFace in ext3.sideFaces:
                (tempBool, normVect) = bRepFace.evaluator.getNormalAtPoint(bRepFace.centroid)
                passed = 0
                if normVect.isParallelTo(yZPlane.geometry.normal):
                    passed += 1
                for edge in bRepFace.edges:
                    if bRepFace.geometry.surfaceType == 0:
                        passed += 1
                        break                            
                

                if(passed == 2):
                    count+=1
                    profTwo = bRepFace

            loftInput = loftFeatures.createInput(adsk.fusion.FeatureOperations.JoinFeatureOperation)
            loftObjects = loftInput.loftSections
            loftObjects.add(profSelect)
            loftObjects.add(profTwo)
            loft1 = loftFeatures.add(loftInput)
            
            selectFace = None
            for bRepFace in ext1.sideFaces:
                (boolVal1, normalVector) = bRepFace.evaluator.getNormalAtPoint(bRepFace.centroid)
                normVect = normalVector.copy()
                xZPlanar = xZPlane.geometry
                xZNorm = xZPlanar.normal
                if normVect.isParallelTo(xZNorm) and bRepFace.centroid.y > 0:
                    selectFace = bRepFace
                    break
            sidePlaneInput = planes.createInput()
            sidePlaneInput.setByTangentAtPoint(selectFace, selectFace.centroid)
            sidePlane = planes.add(sidePlaneInput)
            sideSketch = sketches.add(sidePlane)
            points = []
            points.append(adsk.core.Point3D.create(3.128, -2.1,0))
            points.append(adsk.core.Point3D.create(3.652, -2.1,0))
            points.append(adsk.core.Point3D.create(3.652,-2.246,0))
            points.append(adsk.core.Point3D.create(3.293,-2.246,0))
            points.append(adsk.core.Point3D.create(3.293, -2.466,0))
            points.append(adsk.core.Point3D.create(3.652, -2.466,0))
            points.append(adsk.core.Point3D.create(3.652, -2.61,0))
            points.append(adsk.core.Point3D.create(3.128,-2.61,0))
            lines = []
            for i in range (len(points)):
                points[i] = addPoint(points[i], adsk.core.Point3D.create(-1.152, 1.22,0))
                points[i] = addPoint(points[i], adsk.core.Point3D.create(self._subLength - defaultSubLength,0,0))
            for i in range(len(points)):
                lines.append(sideSketch.sketchCurves.sketchLines.addByTwoPoints(points[i], points[(i+1)%len(points)]))

            sideSketch.sketchCurves.sketchLines.addByTwoPoints(adsk.core.Point3D.create(self._subLength,0,0), points[len(points)-1])
            tempCurve = sideSketch.sketchCurves.sketchLines.addByTwoPoints(adsk.core.Point3D.create(self._subLength,0.6,0),points[1])
            sideSketch.sketchCurves.sketchLines.addByTwoPoints(adsk.core.Point3D.create(self._subLength,0,0), adsk.core.Point3D.create(self._subLength,0.6,0))
            cur = None
            for profile in sideSketch.profiles:
                for profileLoop in profile.profileLoops:
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity == tempCurve:
                            cur = profile
            extLength = adsk.core.ValueInput.createByReal(-0.3)
            ext5 = extrudeFeatures.addSimple(cur, extLength, adsk.fusion.FeatureOperations.JoinFeatureOperation)

            cur = None
            for profile in sideSketch.profiles:
                for profileLoop in profile.profileLoops:
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity == lines[4]:
                            cur = profile
            ext6 = extrudeFeatures.addSimple(cur, extLength, adsk.fusion.FeatureOperations.JoinFeatureOperation)

            strapPoint1 = adsk.core.Point3D.create(0.1, -(0.1 + self._subRadius),0)
            strapPoint2 = adsk.core.Point3D.create(self._subLength-0.1, -(0.3 + self._subRadius), 0)
            rectangle = xYSketch.sketchCurves.sketchLines.addTwoPointRectangle(strapPoint1, strapPoint2)

            selectProfile = None
            strapHoleEx = adsk.core.ValueInput.createByReal(-self._mainRadius)
            for profile in xYSketch.profiles:
                passed = True
                for profileLoop in profile.profileLoops:
                    cur = False
                    for profileCurve in profileLoop.profileCurves:
                        for line in rectangle:
                            if profileCurve.sketchEntity == line:
                                cur = True
                    if cur == False:
                        passed = False
                        break
                if passed:
                    selectProfile = profile


            strapHoleEx = adsk.core.ValueInput.createByReal(-self._mainRadius)
            strapProfile = xYSketch.profiles.item(0)
            ext2 = extrudeFeatures.createInput(selectProfile, adsk.fusion.FeatureOperations.CutFeatureOperation)
            ext2.setDistanceExtent(False, strapHoleEx)
            ext2.participantBodies = [ext1.bodies.item(0)]
            extrudeFeatures.add(ext2)

            temp = self._mainRadius + self._mainThickness
            if(self._mainThickness <= 0.4):
                temp = self._mainRadius + 0.4
            
            offsetValue = -(temp - 0.3 - self._jointTol)

            planeInput = planes.createInput()
            offsetValue = adsk.core.ValueInput.createByReal(offsetValue)
            planeInput.setByOffset(xZPlane, offsetValue)
            sketch3Plane = planes.add(planeInput)
            sketch3 = sketches.add(sketch3Plane)
            jointPoint = adsk.core.Point3D.create(-self._subConnectLength + self._subLength,0.3,0)
            sideCircles = sketch3.sketchCurves.sketchCircles
            jointInnerRing = sideCircles.addByCenterRadius(jointPoint, self._jointRadius - self._jointRotateTol)
            jointOuterRing = sideCircles.addByCenterRadius(jointPoint, self._jointRadius + self._jointThickness)
            points = []
            largeRadius = self._jointRadius + self._jointThickness
            points.append(addPoint(jointPoint,point(0,-largeRadius,0)))
            points.append(addPoint(jointPoint,point(largeRadius,-largeRadius,0)))
            points.append(addPoint(jointPoint,point(largeRadius,largeRadius,0)))
            points.append(addPoint(jointPoint,point(0,largeRadius,0)))
            lines = []
            for i in range(3):
                lines.append(sketch3.sketchCurves.sketchLines.addByTwoPoints(points[i],points[i+1]))
            
            profs = adsk.core.ObjectCollection.create()
            for profile in sketch3.profiles:
                profs.add(profile)
            
            extLength = adsk.core.ValueInput.createByReal(0.3)
            ext3 = extrudeFeatures.addSimple(profs, extLength, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extLengthOp = adsk.core.ValueInput.createByReal(-(0.3 + self._jointTol))
            selectProf = None
            for profile in sketch3.profiles:
                for profileLoop in profile.profileLoops:
                    check = False
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity == jointInnerRing :
                            check = True
                    if check and profileLoop.profileCurves.count == 1 and profile.profileLoops.count == 1:
                        selectProf = profile
            ext4 = extrudeFeatures.addSimple(selectProf, extLengthOp, adsk.fusion.FeatureOperations.JoinFeatureOperation)
            
            largeRadius = self._subRadius + self._mainThickness + self._intersectLength
            cutLine = sketch4.sketchCurves.sketchLines.addByTwoPoints(center, point(math.cos(degToRad(-45))* largeRadius, math.sin(degToRad(-45)) * largeRadius,0))
            profSelect = adsk.core.ObjectCollection.create()
            count = 0
            for profile in sketch4.profiles:
                for profileLoop in profile.profileLoops:
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity.objectType == sketch4.sketchCurves.sketchLines.item(0).classType():
                            curve = profileCurve.sketchEntity
                            curveVector = curve.worldGeometry.asInfiniteLine().direction
                            zVector = self.comp2.zConstructionAxis.geometry.direction
                            sketchPoint = curve.endSketchPoint.worldGeometry

                            if curveVector.isParallelTo(zVector) and sketchPoint.y < 0 and curve.length == 0.6:
                                profSelect.add(profile)

            count = 0
            profTwo = None
            for bRepFace in ext3.sideFaces:
                (tempBool, normVect) = bRepFace.evaluator.getNormalAtPoint(bRepFace.centroid)
                passed = 0
                if normVect.isParallelTo(yZPlane.geometry.normal):
                    passed += 1
                for edge in bRepFace.edges:
                    if bRepFace.geometry.surfaceType == 0:
                        passed += 1
                        break                            
                

                if(passed == 2):
                    count+=1
                    profTwo = bRepFace

            loftInput = loftFeatures.createInput(adsk.fusion.FeatureOperations.JoinFeatureOperation)
            loftObjects = loftInput.loftSections
            loftObjects.add(profSelect)
            loftObjects.add(profTwo)
            loft1 = loftFeatures.add(loftInput)

            #sketch 5 rubber band connector
            selectFace = None
            for bRepFace in ext1.sideFaces:
                (boolVal1, normalVector) = bRepFace.evaluator.getNormalAtPoint(bRepFace.centroid)
                normVect = normalVector.copy()
                xZPlanar = xZPlane.geometry
                xZNorm = xZPlanar.normal
                if normVect.isParallelTo(xZNorm) and bRepFace.centroid.y < 0:
                    selectFace = bRepFace
                    break
            sidePlaneInput = planes.createInput()
            sidePlaneInput.setByTangentAtPoint(selectFace, selectFace.centroid)
            sidePlane = planes.add(sidePlaneInput)
            sideSketch = sketches.add(sidePlane)
            points = []
            points.append(adsk.core.Point3D.create(3.128, -2.1,0))
            points.append(adsk.core.Point3D.create(3.652, -2.1,0))
            points.append(adsk.core.Point3D.create(3.652,-2.246,0))
            points.append(adsk.core.Point3D.create(3.293,-2.246,0))
            points.append(adsk.core.Point3D.create(3.293, -2.466,0))
            points.append(adsk.core.Point3D.create(3.652, -2.466,0))
            points.append(adsk.core.Point3D.create(3.652, -2.61,0))
            points.append(adsk.core.Point3D.create(3.128,-2.61,0))
            lines = []
            for i in range (len(points)):
                points[i] = addPoint(points[i], adsk.core.Point3D.create(-1.152, 1.22,0))
                points[i] = addPoint(points[i], adsk.core.Point3D.create(self._subLength - defaultSubLength,0,0))
                points[i].y = -points[i].y
            for i in range(len(points)):
                lines.append(sideSketch.sketchCurves.sketchLines.addByTwoPoints(points[i], points[(i+1)%len(points)]))
            sideSketch.sketchCurves.sketchLines.addByTwoPoints(adsk.core.Point3D.create(self._subLength,0,0), points[len(points)-1])
            tempCurve = sideSketch.sketchCurves.sketchLines.addByTwoPoints(adsk.core.Point3D.create(self._subLength,-0.6,0),points[1])
            sideSketch.sketchCurves.sketchLines.addByTwoPoints(adsk.core.Point3D.create(self._subLength,0,0), adsk.core.Point3D.create(self._subLength,-0.6,0))
            cur = None
            for profile in sideSketch.profiles:
                for profileLoop in profile.profileLoops:
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity == tempCurve:
                            cur = profile
            extLength = adsk.core.ValueInput.createByReal(-0.3)
            ext5 = extrudeFeatures.addSimple(cur, extLength, adsk.fusion.FeatureOperations.JoinFeatureOperation)
            cur = None
            for profile in sideSketch.profiles:
                for profileLoop in profile.profileLoops:
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity == lines[4]:
                            cur = profile
            ext6 = extrudeFeatures.addSimple(cur, extLength, adsk.fusion.FeatureOperations.JoinFeatureOperation)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def assemble(self):
        try:
            rootComponent = design.rootComponent
            joints = rootComponent.joints
            selectEdgeOne = None
            if self._ref1 == None:
                ui.messageBox("here")
            geo1 = adsk.fusion.JointGeometry.createByCurve(self._ref1, adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
            geo2 = adsk.fusion.JointGeometry.createByProfile(self._ref2, None, adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
            jointInput = joints.createInput(geo1, geo2)


            jointInput.isFlipped = False
            offset = adsk.core.ValueInput.createByReal((0.3 + self._jointTol))
            jointInput.offset = offset
            jointInput.setAsRevoluteJointMotion(adsk.fusion.JointDirections.ZAxisJointDirection)
            joint = joints.add(jointInput)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        commandDefinitions = ui.commandDefinitions
        cmdDef = commandDefinitions.itemById('Splint')
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition('Splint', 
                                                            'Create Splint', 
                                                            'Create a Splint')
        else:
            ui.messageBox("Didn't Create a new command definitions")

        onCommandCreated = MyCommandCreatedEventHandler()
        cmdDef.commandCreated.add(onCommandCreated)

        handlers.append(onCommandCreated)       
        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)
        
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))