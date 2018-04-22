# encoding: utf-8

import gvsig

from javax.swing.table import AbstractTableModel
from org.gvsig.fmap.geom.primitive import Point
from org.gvsig.tools import ToolsLocator

def getPointsStorage():
  try:
    from org.gvsig.temporarystorage import TemporaryStorageLocator
    manager = TemporaryStorageLocator.getTemporaryStorageManager()
  except:
    print "WARNING: Can¡t retrieve TemporaryStorageManager"
    return None
  storage = manager.create("Points",Point)
  return storage
  
class CoordinateStorageModel(AbstractTableModel):
  def __init__(self):
    AbstractTableModel.__init__(self)
    i18n = ToolsLocator.getI18nManager()
    self.__columnNames = (
      i18n.getTranslation("_Name"),
      i18n.getTranslation("_X"),
      i18n.getTranslation("_Y")
    )
    self.__storage = getPointsStorage()

  def isPointStorageAvailable(self):
    return self.__storage!=None
    
  def getColumnCount(self):
    return 3

  def getColumnName(self, index):
    return self.__columnNames[index]

  def getValueAt(self, rowIndex, columnIndex):
    if self.__storage == None:
      return ""
    row = self.__storage.asList()[rowIndex]
    if columnIndex==0:
      return row.getKey()
    if columnIndex==1:
      return row.getValue().getX()
    if columnIndex==2:
      return row.getValue().getY()
    return ""
    
  def getRowCount(self):
    if self.__storage == None:
      return 0
    return self.__storage.asList().size()
    
  def addPoint(self, pointName, point):
    if self.__storage == None:
      return 
    self.__storage.put(pointName,point)
    self.fireTableDataChanged()

  def removeRow(self, row):
    if self.__storage == None:
      return 
    pointName = self.getValueAt(row,0)
    self.__storage.remove(pointName)
    self.fireTableDataChanged()
    
  def getPointOfRow(self, row):
    if self.__storage == None:
      return None
    pointName = self.getValueAt(row,0)
    point = self.__storage.get(pointName)
    return point
    
  def getNameOfRow(self, row):
    if self.__storage == None:
      return None
    pointName = self.getValueAt(row,0)
    return pointName
    
  def setNameOfRow(self, row, pointName):
    if self.__storage == None:
      return 
    oldPointName = self.getValueAt(row,0)
    point = self.__storage.get(oldPointName)
    self.__storage.remove(oldPointName)
    self.__storage.put(pointName,point)
    self.fireTableDataChanged()

    