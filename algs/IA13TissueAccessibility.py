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
__date__ = '2020-01-27'
__copyright__ = '(C) 2019 by LlactaLAB'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsProcessing,
                       QgsProcessingMultiStepFeedback,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink)
from .ZProcesses import *
from .Zettings import *
from .ZHelpers import *

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]

class IA13TissueAccessibility(QgsProcessingAlgorithm):
    """
    Mide el grado en que la estructura interna de un área se
    relaciona con el sistema a mayor escala en el que se encuentra.
    """

    ROADS_SINTAXIS = 'ROADS_SINTAXIS'
    FIELD_SINTAXIS = 'FIELD_SINTAXIS'
    CELL_SIZE = 'CELL_SIZE'
    OUTPUT = 'OUTPUT'
    STUDY_AREA_GRID = 'STUDY_AREA_GRID'


    def initAlgorithm(self, config):

        currentPath = getCurrentPath(self)
        FULL_PATH = buildFullPathName(currentPath, nameWithOuputExtension(NAMES_INDEX['IA13'][1]))

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.ROADS_SINTAXIS,
                self.tr('Vías SINTAXIS ESPACIAL'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_SINTAXIS,
                self.tr('Valor'),
                'NACH_slen', 'ROADS_SINTAXIS'
            )
        )        

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.STUDY_AREA_GRID,
                self.tr(TEXT_GRID_INPUT),
                [QgsProcessing.TypeVectorPolygon],
                '', OPTIONAL_GRID_INPUT
            )
        )

        if OPTIONAL_GRID_INPUT:
            self.addParameter(
                QgsProcessingParameterNumber(
                    self.CELL_SIZE,
                    self.tr('Tamaño de la malla'),
                    QgsProcessingParameterNumber.Integer,
                    P_CELL_SIZE, False, 1, 99999999
                )
            )


        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Salida'),
                QgsProcessing.TypeVectorAnyGeometry,
                str(FULL_PATH)
            )
        )

    def processAlgorithm(self, params, context, feedback):
        steps = 0
        totalStpes = 11
        fieldSintaxis = params['FIELD_SINTAXIS']

        feedback = QgsProcessingMultiStepFeedback(totalStpes, feedback)


        steps = steps+1
        feedback.setCurrentStep(steps)
        if not OPTIONAL_GRID_INPUT: params['CELL_SIZE'] = P_CELL_SIZE
        grid, isStudyArea = buildStudyArea(params['CELL_SIZE'], params['ROADS_SINTAXIS'],
                                           params['STUDY_AREA_GRID'],
                                           context, feedback)
        gridNeto = grid

        steps = steps+1
        feedback.setCurrentStep(steps)
        centroides = createCentroids(params['ROADS_SINTAXIS'], context, feedback)


        steps = steps+1
        feedback.setCurrentStep(steps)
        result = joinByLocation(gridNeto['OUTPUT'],
                                             centroides['OUTPUT'],
                                             [fieldSintaxis],                                   
                                              [CONTIENE], [MEDIA],
                                              UNDISCARD_NONMATCHING,
                                              context,
                                              feedback)   

        steps = steps+1
        feedback.setCurrentStep(steps)
        formulaDummy = fieldSintaxis+'_mean * 1.00'
        result = calculateField(result['OUTPUT'],
                                   NAMES_INDEX['IA13'][0],
                                   formulaDummy,
                                   context,
                                   feedback, params['OUTPUT'])



        return result



    def icon(self):
        return QIcon(os.path.join(pluginPath, 'sisurbano', 'icons', 'tejido2.png'))

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'A13 Accesibilidad al tejido'

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
        return 'A Ambiente construido'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return IA13TissueAccessibility()

    def shortHelpString(self):
        return  "<b>Descripción:</b><br/>"\
                "<span>Mide el grado en que la estructura interna de un área se relaciona con el sistema a mayor escala en el que se encuentra.</span>"\
                "<br/><br/><b>Justificación y metodología:</b><br/>"\
                "<span>Relación entre radio 3 / radio n. Como radio local se utiliza 1200m (caminata de 15min).</span>"\
                "<br/><br/><b>Formula:</b><br/>"\
                "<span>Preproceso de sintaxis espacial</span><br/>"