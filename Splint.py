#Author-
#Description-
import splintModule
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

class MyCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs

            splint = splintModule.Splint()
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



def run(context):
    try:
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        commandDefinitions = ui.commandDefinitions
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
