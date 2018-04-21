# encoding: utf-8

import gvsig

from gvsig import getResource

from java.io import File
from org.gvsig.andami import PluginsLocator
from org.gvsig.app import ApplicationLocator
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.tools import ToolsLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator

from addons.CoordinateCapture.coordinatecapture import showCoordinateCapture

class CoordinateCaptureExtension(ScriptingExtension):
  def __init__(self):
    pass

  def canQueryByAction(self):
    return True

  def isEnabled(self,action):
    return True

  def isVisible(self,action):
    return True
    
  def execute(self,actionCommand, *args):
    actionCommand = actionCommand.lower()
    if actionCommand == "view-query-coordinate-capture":
      showCoordinateCapture()

def selfRegister():
  application = ApplicationLocator.getManager()

  #
  # Registramos las traducciones
  i18n = ToolsLocator.getI18nManager()
  i18n.addResourceFamily("text",File(getResource(__file__,"i18n")))

  #
  # Registramos los iconos en el tema de iconos
  icon = File(getResource(__file__,"images","view-query-coordinate-capture.png")).toURI().toURL()
  iconTheme = ToolsSwingLocator.getIconThemeManager().getCurrent()
  iconTheme.registerDefault("scripting.CoordinateCaptureExtension", "action", "view-query-coordinate-capture", None, icon)

  #
  # Creamos la accion 
  extension = CoordinateCaptureExtension()
  actionManager = PluginsLocator.getActionInfoManager()
  action = actionManager.createAction(
    extension, 
    "view-query-coordinate-capture", # Action name
    "Coordinate capture", # Text
    "view-query-coordinate-capture", # Action command
    "view-query-coordinate-capture", # Icon name
    None, # Accelerator
    650700600, # Position 
    "_Show_the_coordinate_capture" # Tooltip
  )
  action = actionManager.registerAction(action)
  application.addMenu(action, "View/Query/Coordinate capture")
  

      
