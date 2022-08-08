#Author-
#Description-
import adsk.core, adsk.fusion, adsk.cam, traceback
import math

app = adsk.core.Application.get()
ui = app.userInterface
handlers = []
selectedEdges = []
defaultMainDiameter = 2.5
defaultMainThickness = 0.3
defaultMainLength = 1.0
defaultConnectLength = 2.0
defaultJointRadius = 0.27
defaultJointThickness = 0.23

def createNewComponent():
    # Get the active design.
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
                elif input.id == 'jointRadius':
                    splint.jointRadius = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'jointThickness':
                    splint.jointThickness = unitsMgr.evaluateExpression(input.expression, "cm")
            splint.buildSplint()
            args.isValidResult = True
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
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
            initJointRadius = adsk.core.ValueInput.createByReal(defaultJointRadius)
            inputs.addValueInput('jointRadius', 'Joint Radius', 'cm', initJointRadius)
            initJointThickness = adsk.core.ValueInput.createByReal(defaultJointThickness)
            inputs.addValueInput('jointThickness', 'Joint Thickness', 'cm', initJointThickness)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class Splint:
    def __init__(self):
        self._mainRadius = defaultMainDiameter/2
        self._mainThickness = defaultMainThickness
        self._mainLength = defaultMainLength
        self._connectLength = defaultConnectLength 
        self._jointRadius = defaultJointRadius
        self._jointThickness = defaultJointThickness
        self._intersectLength = 0.01

    @property
    def mainRadius(self):
        return self._mainRadius
    @mainRadius.setter
    def mainRadius(self, value):
        self._mainRadius = value

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

    def buildSplint(self):
        try:
            global newComp
            newComp = createNewComponent()
            if newComp is None:
                ui.messageBox("New Component Failed to Create")

            sketches = newComp.sketches
            features = newComp.features
            planes = newComp.constructionPlanes
            extrudeFeatures = features.extrudeFeatures
            loftFeatures = features.loftFeatures
            #sketch 1
            yZPlane = newComp.yZConstructionPlane
            xYPlane = newComp.xYConstructionPlane
            xZPlane = newComp.xZConstructionPlane
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
            #yz plane being used
            point3 = adsk.core.Point3D.create(0.6,temp,0)
            point4 = adsk.core.Point3D.create(0.6,-temp,0)
            yZSketch.sketchCurves.sketchLines.addByTwoPoints(point1, point3)
            yZSketch.sketchCurves.sketchLines.addByTwoPoints(point2, point4)
            mainLine = yZSketch.sketchCurves.sketchLines.addByTwoPoints(point3, point4)
            
            #extrude 1
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
            mainLength = adsk.core.ValueInput.createByReal(self._mainLength) #input parameters here
    
            ext1 = extrudeFeatures.addSimple(extProfs,mainLength, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            #sketch2
            strapPoint1 = adsk.core.Point3D.create(0.1, 0.1 + self._mainRadius,0)
            strapPoint2 = adsk.core.Point3D.create(self._mainLength-0.1, 0.3 + self._mainRadius, 0)
            xYSketch.sketchCurves.sketchLines.addTwoPointRectangle(strapPoint1, strapPoint2)

            #extrude2
            strapHoleEx = adsk.core.ValueInput.createByReal(-self._mainRadius)
            strapProfile = xYSketch.profiles.item(0)
            ext2 = extrudeFeatures.addSimple(strapProfile, strapHoleEx, adsk.fusion.FeatureOperations.CutFeatureOperation)
            
            selectFace = None
            for bRepFace in ext1.sideFaces:
                (boolVal1, normalVector) = bRepFace.evaluator.getNormalAtPoint(bRepFace.centroid)
                normVect = normalVector.copy()
                xZPlanar = xZPlane.geometry
                xZNorm = xZPlanar.normal
                #ui.messageBox("normVect " + stringVector(normVect)+ "\nxZNorm " + stringVector(xZNorm))
                if normVect.isParallelTo(xZNorm) and bRepFace.centroid.y > 0:
                    selectFace = bRepFace
                    #ui.messageBox("Found")
                    break

            #sketch 3
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

            #ext3
            extProfs = adsk.core.ObjectCollection.create()
            for profile in sideSketch.profiles:
                for profileLoop in profile.profileLoops:
                    check = False
                    for profileCurve in profileLoop.profileCurves:
                        if profileCurve.sketchEntity == jointOuterRing:
                            check = True

                    if check:
                        extProfs.add(profile)
            extLength = adsk.core.ValueInput.createByReal(-0.2)
            ext3 = extrudeFeatures.addSimple(extProfs, extLength, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

            #sketch 4
            planeInput = planes.createInput()
            offsetValue = adsk.core.ValueInput.createByReal(self._mainLength)
            planeInput.setByOffset(yZPlane, offsetValue)
            sketch4Plane = planes.add(planeInput)
            sketch4 = sketches.add(sketch4Plane)
            mainBody = ext1.bodies.item(0)
            selectFace = []
            for bRepFace in mainBody.faces:
                (boolVal1, normalVector) = bRepFace.evaluator.getNormalAtPoint(bRepFace.centroid)
                normVect = normalVector.copy()
                yZPlanar = yZPlane.geometry
                yZNorm = yZPlanar.normal
                if yZNorm.isParallelTo(normVect) and bRepFace.centroid.x == 1.0:
                    selectFace.append(bRepFace)

            projectedEntities = sketch4.intersectWithSketchPlane(selectFace)
            largeRadius = self._mainRadius + self._mainThickness + self._intersectLength
            cutLine = sketch4.sketchCurves.sketchLines.addByTwoPoints(center, point(math.cos(degToRad(45))* largeRadius, math.sin(degToRad(45)) * largeRadius,0))

            #Loft
            profSelect = adsk.core.ObjectCollection.create()
            count =0
            for profile in sketch4.profiles:
                for profileLoop in profile.profileLoops:
                    for profileCurve in profileLoop.profileCurves:
                        #ui.messageBox("ObjectType : {}, classType: {}".format(str(profileCurve.sketchEntity.objectType), str(sketch4.sketchCurves.sketchLines.item(0).classType())))
                        if profileCurve.sketchEntity.objectType == sketch4.sketchCurves.sketchLines.item(0).classType():
                            curve = profileCurve.sketchEntity
                            curveVector = curve.worldGeometry.asInfiniteLine().direction
                            zVector = newComp.zConstructionAxis.geometry.direction
                            sketchPoint = curve.endSketchPoint.worldGeometry
                            #ui.messageBox(stringVector(curveVector) + "\nConstruction Vector: " + stringVector(zVector) + "\nPos: {}, {}, {}".format(sketchPoint.x, sketchPoint.y, sketchPoint.z))

                            if curveVector.isParallelTo(zVector) and curve.length == 0.6:
                                count+=1
                            if curveVector.isParallelTo(zVector) and sketchPoint.y > 0 and curve.length == 0.6:
                                profSelect.add(profile)
            count = 0
            for bRepFace in ext3.sideFaces:
                (tempBool, normVect) = bRepFace.evaluator.getNormalAtPoint(bRepFace.centroid)
                edges = bRepFace.edges
                passed = 0

                if normVect.isParallelTo(yZPlane.geometry.normal):
                    passed += 1
                for edge in bRepFace.edges:
                    (boolTemp, startPoint, endPoint) = edge.evaluator.getEndPoints()
                    if startPoint.x == self._connectLength - self._jointRadius - self._jointThickness:
                        if bRepFace.geometry.surfaceType == 0:
                            passed += 1
                            break                            
                

                if(passed == 2):
                    count+=1
                    ui.messageBox(stringVector(normVect) + "\nConstruction Vector: " + stringVector(yZPlane.geometry.normal) + "\n" + stringVector(bRepFace.centroid))
                    profTwo = bRepFace
            loftInput = loftFeatures.createInput(adsk.fusion.FeatureOperations.JoinFeatureOperation)
            loftObjects = loftInput.loftSections
            loftObjects.add(profSelect)
            loftObjects.add(profTwo)
            loft1 = loftFeatures.add(loftInput)

            #mirror
            mirrorFeatures = features.mirrorFeatures
            inputEntities = adsk.core.ObjectCollection.create()
            inputEntities.add(ext2)
            inputEntities.add(ext3)
            inputEntities.add(loft1)
            mirrorInput = mirrorFeatures.createInput(inputEntities, xZPlane)
            mirrorFeatures.add(mirrorInput)



        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        commandDefinitions = ui.commandDefinitions
        ui.messageBox("Start")
        cmdDef = commandDefinitions.itemById('Splint')
        if not cmdDef:
            ui.messageBox("Create a new command definitions")
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
        ui.messageBox("Done")
        
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
