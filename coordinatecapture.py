# encoding: utf-8

import gvsig

from addons.CoordinateCapture.patchs.fixformpanel import fixFormPanelResourceLoader
from addons.CoordinateCapture.coordinatestorage import CoordinateStorageModel
from gvsig import currentView
from gvsig import getResource
from gvsig.commonsdialog import msgbox
from gvsig.libs.formpanel import FormPanel
from java.awt import Toolkit
from java.awt.datatransfer import StringSelection
from java.awt.event import ComponentAdapter
from java.io import File
from java.util import Vector
from javax.swing.table import DefaultTableModel
from org.gvsig.andami import IconThemeHelper
from org.gvsig.app.gui.panels import CRSSelectPanelFactory
from org.gvsig.fmap.mapcontrol.tools.Behavior import PointBehavior
from org.gvsig.fmap.mapcontrol.tools.Listeners import PointListener
from org.gvsig.tools import ToolsLocator
from org.gvsig.tools.swing.api import Component
from org.gvsig.tools.swing.api import ToolsSwingLocator
from org.gvsig.tools.swing.api.windowmanager import WindowManager

from gvsig.commonsdialog import inputbox
from gvsig.commonsdialog import QUESTION

from javax.swing import ListSelectionModel

from gvsig.commonsdialog import confirmDialog
from gvsig.commonsdialog import YES
from gvsig.commonsdialog import YES_NO

class ClosePanelListener(ComponentAdapter):
  def __init__(self, coordinateCapturePanel):
    ComponentAdapter.__init__(self)
    self.coordinateCapturePanel = coordinateCapturePanel

  def componentHidden(self, event):
    self.coordinateCapturePanel.endCapture()
    
class CoordinateCapturePanel(FormPanel, PointListener,Component):
  def __init__(self):
    FormPanel.__init__(self,getResource(__file__,"coordinatecapture.xml"))
    i18n = ToolsLocator.getI18nManager()
    self.setPreferredSize(320,180)
    self.mapControl = None
    self.previousTool = None
    self.transform = None
    self.crs = None
    self.lastPoint = None
    self.translateUI()

    self.asJComponent().addComponentListener(ClosePanelListener(self))
    
    self.btnToggleCapture.setText(i18n.getTranslation("_Start_points_capture"))
    self.btnClearCRS.setEnabled(False)
    self.btnCRS.setEnabled(False)

    self.__tablemodel = CoordinateStorageModel()
    self.tblPoints.setModel(self.__tablemodel)
    self.btnCopySelectedPoint.setEnabled(False)
    self.btnRenameSelectedPoint.setEnabled(False)
    self.btnDeleteSelectedPoint.setEnabled(False)
    self.btnAddCapturedPoint.setEnabled(False)
    
    self.tabCapturePoint.setEnabledAt(1, self.__tablemodel.isPointStorageAvailable())

    self.tblPoints.getSelectionModel().addListSelectionListener(self.tblPoints_selectionChange)
    self.tblPoints.getSelectionModel().setSelectionMode(ListSelectionModel.SINGLE_INTERVAL_SELECTION)
    
  def translateUI(self):
    #manager = ToolsSwingLocator.getToolsSwingManager()
    from addons.CoordinateCapture.patchs.fixtranslatecomponent import TranslateComponent as manager
    
    for component in ( 
        self.btnCopyToClipboard,
        self.btnToggleCapture,
        self.btnClearCRS,
        self.btnCRS,
        self.btnCopySelectedPoint,
        self.btnRenameSelectedPoint,
        self.btnDeleteSelectedPoint,
        self.btnAddCapturedPoint,
        self.tabCapturePoint
      ):
      manager.translate(component)

  def tblPoints_selectionChange(self, event):
    if event.getValueIsAdjusting():
      return
    row = self.tblPoints.getSelectedRow()
    enabled = row>=0
    self.btnDeleteSelectedPoint.setEnabled(enabled)
    self.btnCopySelectedPoint.setEnabled(enabled)
    self.btnRenameSelectedPoint.setEnabled(enabled)
        
  def btnToggleCapture_click(self,event):
    if self.mapControl == None:
      self.startCapture()
    else:  
      self.endCapture()

  def startCapture(self):
    if self.mapControl != None:
      return
    i18n = ToolsLocator.getI18nManager()
    viewdoc = currentView()
    if viewdoc == None:
      msgbox(i18n.getTranslation("_Must_have_an_active_View"))
      return
    self.mapControl = viewdoc.getWindowOfView().getMapControl()
    self.previousTool = self.mapControl.getCurrentTool()
    self.mapControl.addBehavior("CoordinateCaptureTool", PointBehavior(self))
    self.mapControl.setTool("CoordinateCaptureTool")
    self.btnToggleCapture.setText(i18n.getTranslation("_End_points_capture"))
    if self.crs == None:
      self.crs = self.mapControl.getProjection()
      self.transform = None
    elif self.crs == self.mapControl.getProjection():
      self.transform = None
    else:
      self.transform = self.mapControl.getProjection().getCT(self.crs)
    self.txtCRS.setText(self.crs.getAbrev())
    self.btnClearCRS.setEnabled(True)
    self.btnCRS.setEnabled(True)

  def endCapture(self):
    if self.mapControl == None:
      return
    i18n = ToolsLocator.getI18nManager()
    self.mapControl.setTool(self.previousTool)
    self.btnToggleCapture.setText(i18n.getTranslation("_Start_points_capture"))
    self.mapControl = None
    self.btnClearCRS.setEnabled(False)
    self.btnCRS.setEnabled(False)
  
  def btnCopyToClipboard_click(self, event):
    if self.lastPoint == None:
      return
    s = "%s %s" % (self.txtX.getText(), self.txtY.getText())
    ss = StringSelection(s)
    clpbrd = Toolkit.getDefaultToolkit().getSystemClipboard()
    clpbrd.setContents(ss, None)

  def btnClearCRS_click(self,event):
    if self.mapControl == None:
      return
    self.crs = self.mapControl.getProjection()
    self.transform = None
    self.txtCRS.setText(self.crs.getAbrev())
    self.updatePointInForm()

  def updatePointInForm(self):
    if self.lastPoint == None:
      return
    p = self.lastPoint.cloneGeometry()
    if self.transform != None:
      p.reProject(self.transform)
    self.txtX.setText(str(p.getX()))
    self.txtY.setText(str(p.getY()))
    self.btnAddCapturedPoint.setEnabled(True)
  
  def point(self, event):
    """Evento de PointListener"""
    self.lastPoint = event.getMapPoint()
    self.updatePointInForm()

  def pointDoubleClick(self, event):
    """Evento de PointListener"""
    self.lastPoint = event.getMapPoint()
    self.updatePointInForm()

  def getImageCursor(self):
    """Evento de PointListener"""
    return IconThemeHelper.getImage("cursor-select-by-point")

  def cancelDrawing(self):
    """Evento de PointListener"""
    return False
    
  def btnCRS_click(self,*args):
    i18n = ToolsLocator.getI18nManager()
    title=i18n.getTranslation("_Select_the_reference_system")
    csSelect = CRSSelectPanelFactory.getUIFactory().getSelectCrsPanel(self.crs, True)
    ToolsSwingLocator.getWindowManager().showWindow(csSelect, title, WindowManager.MODE.DIALOG)
    if csSelect.isOkPressed():
      self.transform = None
      self.crs = csSelect.getProjection()
      self.txtCRS.setText(self.crs.getAbrev())
      if self.mapControl!=None:
        if self.mapControl.getProjection()==self.crs:
          self.transform = None
        else:
          self.transform = self.mapControl.getProjection().getCT(self.crs)
      self.updatePointInForm()

  def btnAddCapturedPoint_click(self,event):
    if not self.__tablemodel.isPointStorageAvailable():
      return
    i18n = ToolsLocator.getI18nManager()
    pointName = inputbox(
      i18n.getTranslation("_Point_name"),
      getTitle(),
      messageType=QUESTION, 
      initialValue=""
    )
    if pointName in ("",None):
      return
    self.__tablemodel.addPoint(pointName, self.lastPoint)

  def btnDeleteSelectedPoint_click(self,event):
    if not self.__tablemodel.isPointStorageAvailable():
      return
    i18n = ToolsLocator.getI18nManager()
    if confirmDialog(
      i18n.getTranslation("_Are_you_sure_you_want_to_delete_point"),
      getTitle(),
      optionType=YES_NO,
      messageType=QUESTION
      )!=YES:
      return
    row = self.tblPoints.getSelectedRow()
    if row <0:
      return
    self.__tablemodel.removeRow(row)
    
  def btnRenameSelectedPoint_click(self, event):
    if not self.__tablemodel.isPointStorageAvailable():
      return
    row = self.tblPoints.getSelectedRow()
    if row <0:
      return
    i18n = ToolsLocator.getI18nManager()
    pointName = self.__tablemodel.getNameOfRow(row)
    if pointName == None:
      msgbox(i18n.getTranslation("_Cant_rename_point_of_selected_row"))
      return
    pointName = inputbox(
      i18n.getTranslation("_Point_name"),
      getTitle(),
      messageType=QUESTION, 
      initialValue=pointName
    )
    if pointName in ("",None):
      return
    self.__tablemodel.setNameOfRow(row, pointName)

  def btnCopySelectedPoint_click(self,event):
    if not self.__tablemodel.isPointStorageAvailable():
      return
    row = self.tblPoints.getSelectedRow()
    if row <0:
      return
    p = self.__tablemodel.getPointOfRow(row)
    if p == None:
      return
    s = "%s %s" % (p.getX(), p.getY())
    ss = StringSelection(s)
    clpbrd = Toolkit.getDefaultToolkit().getSystemClipboard()
    clpbrd.setContents(ss, None)
    
    
def getTitle():
  i18n = ToolsLocator.getI18nManager()
  title=i18n.getTranslation("_Coordinate_capture")
  return title


def showCoordinateCapture():
  fixFormPanelResourceLoader()

  p = CoordinateCapturePanel()
  i18n = ToolsLocator.getI18nManager()
  title=i18n.getTranslation("_Coordinate_capture")
  p.showTool(title)

def main(*args):
  showCoordinateCapture()
  