# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Sisurbano
                                 A QGIS plugin
 Cáculo de indicadores urbanos
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-09-16
        copyright            : (C) 2019 by LlactaLAB
        email                : johnatan.astudillo@ucuenca.edu.ec
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Johnatan Astudillo'
__date__ = '2019-09-16'
__copyright__ = '(C) 2019 by LlactaLAB'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
from qgis.utils import iface
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsProcessing,
                       QgsProcessingMultiStepFeedback,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFeatureSink)
from .ZProcesses import *
from .Zettings import *
from .ZHelpers import *

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]

def lineal(params, context, feedback):
  steps = 0
  totalStpes = 1
  pointA = params['A']
  pointB = params['B']
  pointC = params['C']
  pointD = params['D']
  value = params['VALUE']
  feedback = QgsProcessingMultiStepFeedback(totalStpes, feedback)
  #feedback.pushConsoleInfo(str(typeFunction))
  steps = steps+1
  feedback.setCurrentStep(steps)
  formulaLineal = calculateLineal(value, pointA, pointB, pointC, pointD)
  feedback.pushConsoleInfo(str(formulaLineal))
  fieldOputName = "n_" + value
  proximity2OpenSpace = calculateField(params['GRID'], fieldOputName,
                                     formulaLineal,
                                     context,
                                     feedback,  params['OUTPUT'])   

  return proximity2OpenSpace                                 
                                     

def calculateLineal(x, a, b, c, d):
    if c == d: 
        return linearIncrease(x, a, b)
    elif a == b:
        return linearDecrease(x, c, d)
    elif a < b and b < c and  c < d:
        return linearIncreaseAndDecrease(x, a, b, c, d)
    elif a < b and b == c and c < d:
        return linearTriangularIncreaseAndDecrease(x, a, b, c, d)    
    else:
        return "error"


def linearIncrease(x, a, b):
    # x = "(coalesce("+x+",0))"
    a = str(a)
    b = str(b)
    result = "CASE WHEN " + x + " < " + a + " THEN 0 " + \
            "WHEN " + x + " > " + b + " THEN 1 " + \
            "ELSE (" + x + "-" + a +") / ("+ b +"-" + a + ") " + \
            "END"
    return result


def linearDecrease(x, c, d):
    # x = "(coalesce("+x+",0))"
    c = str(c)
    d = str(d)
    result = "CASE WHEN " + x + " > " + d + " THEN 0 " + \
            "WHEN " + x + " < " + c + " THEN 1 " + \
            "ELSE (" + d + "-" + x +") / ("+ d +"-" + c + ") " + \
            "END"
    return result
 

def linearIncreaseAndDecrease(x, a, b, c, d):
    # x = "(coalesce("+x+",0))"
    a = str(a)
    b = str(b)
    c = str(c)
    d = str(d)    
    result = "CASE WHEN " + x + " < " + a + " THEN 0 " + \
            "WHEN " + x + " >  " + d + " THEN 0 " + \
            "WHEN " + x + " >= " + b + " AND " + x + " <= " + c  + " THEN 1 " + \
            "WHEN " + x + " >= " + a + " AND " + x + " <= " + b  + " THEN (" + x + "-" + a +") / ("+ b +"-" + a + ") " + \
            "ELSE (" + d + "-" + x +") / ("+ d +"-" + c + ") " + \
            "END"
    return result


def linearTriangularIncreaseAndDecrease(x, a, b, c, d):
    # x = "(coalesce("+x+",0))"
    a = str(a)
    b = str(b)
    c = str(c)
    d = str(d)    
    result = "CASE WHEN " + x + " <= " + a + " THEN 0 " + \
            "WHEN " + x + " >  " + d + " THEN 0 " + \
            "WHEN " + x + " > " + a + " AND " + x + " <= " + b  + " THEN (" + x + "-" + a +") / ("+ b +"-" + a + ") " + \
            "ELSE (" + d + "-" + x +") / ("+ d +"-" + c + ") " + \
            "END"
    return result        

class ZN01FuzzyVectorial(QgsProcessingAlgorithm):
    """
    Normalizar una atrubuto de una capa vectorial
    Formula: 
    Lineal
    z = (x - min(x)) / (max(x) - min(x))
    Sigmoid
    y = 1 / (1 + math.exp(-x))
    """  
    GRID = 'GRID'
    VALUE = 'VALUE'
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    FUNCTION = 'FUNCTION'
    OUTPUT = 'OUTPUT'


    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.GRID,
                self.tr('Indicador'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        currentPath = getPath()
        attrName = getPossibleAttrName()
        min, max = getMaxMin(attrName)

        FULL_PATH = buildFullPathName(currentPath, 'n_'+attrName+'.gpkg')

        self.addParameter(
            QgsProcessingParameterField(
                self.VALUE,
                self.tr('Valor'),
                attrName, 'GRID'
            )
        ) 


        self.addParameter(
            QgsProcessingParameterNumber(
                self.A,
                self.tr('A'),
                QgsProcessingParameterNumber.Double,
                min, False, 0, 99999999
            )
        )     


        self.addParameter(
            QgsProcessingParameterNumber(
                self.B,
                self.tr('B'),
                QgsProcessingParameterNumber.Double,
                max, False, 0, 99999999
            )
        )     

        self.addParameter(
            QgsProcessingParameterNumber(
                self.C,
                self.tr('C'),
                QgsProcessingParameterNumber.Double,
                '0', False, 0, 99999999
            )
        ) 

        self.addParameter(
            QgsProcessingParameterNumber(
                self.D,
                self.tr('D'),
                QgsProcessingParameterNumber.Double,
                '0', False, 0, 99999999
            )
        )                  

        # self.addParameter(
        #     QgsProcessingParameterEnum(
        #         self.FUNCTION,
        #         self.tr('Función'),
        #         options=["Lineal"]
        #     )
        # )   

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Salida'),
                QgsProcessing.TypeVectorAnyGeometry,
                str(FULL_PATH)                
            )
        )

    def processAlgorithm(self, params, context, feedback):
      LINEAL = 0
      # typeFunction = params['FUNCTION']   
      typeFunction = 0
      if(typeFunction == LINEAL):
        result = lineal(params, context, feedback)

      return result 


 

  




        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        #return {self.OUTPUT: dest_id}
                                          
    def icon(self):
        return QIcon(os.path.join(pluginPath, 'sisurbano', 'icons', 'normal.png'))

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Z01 Normalizar indicador'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Z General'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ZN01FuzzyVectorial()

    def shortHelpString(self):
        image1 = os.path.join(pluginPath, 'sisurbano', 'icons', 'normalize1.jpg')
        image2 = os.path.join(pluginPath, 'sisurbano', 'icons', 'normalize2.jpg')
        image3 = os.path.join(pluginPath, 'sisurbano', 'icons', 'normalize3.jpg')
        return  "<b>General:</b><br>"\
                "<b>Normalization by linear interpolation: smaller is better (SB).</b><br>"\
                "<img  height='150' src='"+image1+"' /><br>"\
                "<b>Normalization by linear interpolation: larger is better (LB).</b><br>"\
                "<img  height='150' src='"+image2+"' /><br>"\
                "Normailizar indicadores on a given <b>texto en resaltados</b>.<br>"\
                "<img  height='150' src='"+image3+"' /><br>"\
                " Normalization by linear interpolation: nominal is best (NB)</b>.<br>"\
                "<b>Parameters (required):</b><br>"\
                "Los siguientes parametros son necesarios para el algortimo:"\
                "<ul><li>Valor</li><li>Otro Layer</li><li>Unique Point ID Field (numerical)</li></ul><br>"\