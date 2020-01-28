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
__date__ = '2019-12-04'
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

class ID01HousingFullCoverageBasicServices(QgsProcessingAlgorithm):
    """
    Mide el porcentaje de viviendas que tienen acceso directo en su vivienda a
    una fuente de agua potable, energía eléctrica, alcantarillado y recolección de residuos sólidos.
    Formula: (No. viviendas con todos los servicios / No. total de viviendas)*100
    """

    BLOCKS = 'BLOCKS'
    VAR_SECTORES = 'VAR_SECTORES'
    FIELD_POPULATION = 'FIELD_POPULATION'
    FIELD_VAR_SECTORES = 'FIELD_VAR_SECTORES'
    CELL_SIZE = 'CELL_SIZE'
    OUTPUT = 'OUTPUT'
    STUDY_AREA_GRID = 'STUDY_AREA_GRID'


    def initAlgorithm(self, config):

        currentPath = getCurrentPath(self)
        FULL_PATH = buildFullPathName(currentPath, nameWithOuputExtension(NAMES_INDEX['ID01'][1]))

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.BLOCKS,
                self.tr('Manzanas'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_POPULATION,
                self.tr('Población'),
                'poblacion', 'BLOCKS'
            )
        )    

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.VAR_SECTORES,
                self.tr('Sectores'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_VAR_SECTORES,
                self.tr('Viviendas con servicios básicos'),
                'Viviendas_', 'VAR_SECTORES'
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
        totalStpes = 24
        fieldPopulationLast = params['FIELD_POPULATION']
        fieldVarSectores = params['FIELD_VAR_SECTORES']

        feedback = QgsProcessingMultiStepFeedback(totalStpes, feedback)

        varSectores = params['VAR_SECTORES']

        steps = steps+1
        feedback.setCurrentStep(steps)
        if not OPTIONAL_GRID_INPUT: params['CELL_SIZE'] = P_CELL_SIZE
        grid, isStudyArea = buildStudyArea(params['CELL_SIZE'], params['BLOCKS'],
                                           params['STUDY_AREA_GRID'],
                                           context, feedback)
        gridNeto = grid

        steps = steps+1
        feedback.setCurrentStep(steps)
        formula = fieldVarSectores+'* 1'
        varSectores = calculateField(varSectores, 'var_sector',
                                        formula,
                                        context,
                                        feedback)   
      
        varSectores =  varSectores['OUTPUT']    


        steps = steps+1
        feedback.setCurrentStep(steps)        
        varSectores = calculateArea(varSectores, 'area_bloc', context,
                             feedback)


        steps = steps+1
        feedback.setCurrentStep(steps)
        segmentsVarSectores = intersection(varSectores['OUTPUT'], gridNeto['OUTPUT'],
                                ['var_sector','area_bloc'],
                                'id_grid',
                                context, feedback) 


        steps = steps+1
        feedback.setCurrentStep(steps)
        segmentsVarSectoresArea = calculateArea(segmentsVarSectores['OUTPUT'],
                                   'area_seg',
                                   context, feedback)


        steps = steps+1
        feedback.setCurrentStep(steps)
        formulaLastPopulationSegments = '(area_seg/area_bloc) * var_sector'
        beginHousingForSegments = calculateField(segmentsVarSectoresArea['OUTPUT'], 'seg_var_sector',
                                          formulaLastPopulationSegments,
                                          context,
                                          feedback)        


        steps = steps+1
        feedback.setCurrentStep(steps)
        segmentsVarSectoresFixed = makeSureInside(beginHousingForSegments['OUTPUT'],
                                                    context,
                                                    feedback)                                     
        blocks = params['BLOCKS']

        steps = steps+1
        feedback.setCurrentStep(steps)
        formula = fieldPopulationLast+'* 1'
        blocks = calculateField(blocks, 'hou',
                                        formula,
                                        context,
                                        feedback)   
        blocks =  blocks['OUTPUT'] 


        steps = steps+1
        feedback.setCurrentStep(steps)        
        blocks = calculateArea(blocks, 'area_bloc', context,
                             feedback)

        steps = steps+1
        feedback.setCurrentStep(steps)
        segments = intersection(blocks['OUTPUT'] , gridNeto['OUTPUT'],
                                ['area_bloc','hou'],
                                'id_grid',
                                context, feedback)     

        steps = steps+1
        feedback.setCurrentStep(steps)
        segmentsArea = calculateArea(segments['OUTPUT'],
                                   'area_seg',
                                   context, feedback)    

        steps = steps+1
        feedback.setCurrentStep(steps)
        formulaLastPopulationSegments = '(area_seg/area_bloc) * hou'
        housingForSegments = calculateField(segmentsArea['OUTPUT'], 'seg_hou',
                                          formulaLastPopulationSegments,
                                          context,
                                          feedback)                                                                  


        steps = steps+1
        feedback.setCurrentStep(steps)
        segmentsFixed = makeSureInside(housingForSegments['OUTPUT'],
                                                    context,
                                                    feedback)


        steps = steps+1
        feedback.setCurrentStep(steps)
        gridNetoAndSegments = joinByLocation(gridNeto['OUTPUT'],
                                             segmentsFixed['OUTPUT'],
                                              ['seg_hou'],                                   
                                              [CONTIENE], [SUM],
                                              UNDISCARD_NONMATCHING,
                                              context,
                                              feedback)    

      

        steps = steps+1
        feedback.setCurrentStep(steps)
        populations = joinByLocation(gridNetoAndSegments['OUTPUT'],
                                     segmentsVarSectoresFixed['OUTPUT'],
                                      ['seg_var_sector'],                                   
                                      [CONTIENE], [SUM],
                                      UNDISCARD_NONMATCHING,
                                      context,
                                      feedback)  


        formulaProximity = 'coalesce((coalesce(seg_var_sector_sum,0) /  coalesce(seg_hou_sum,""))*100, "")'
        steps = steps+1
        feedback.setCurrentStep(steps)
        result = calculateField(populations['OUTPUT'], NAMES_INDEX['ID01'][0],
                                        formulaProximity,
                                        context,
                                        feedback,  params['OUTPUT'])        



        return result

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        #return {self.OUTPUT: dest_id}

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'sisurbano', 'icons', 'fullservices.jpg'))

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'D01 Viviendas con cobertura total de servicios básicos'

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
        return 'D Dinámicas socio-espaciales'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ID01HousingFullCoverageBasicServices()

    def shortHelpString(self):
        return  "<b>Descripción:</b><br/>"\
                "<span>Mide el porcentaje de viviendas que tienen acceso directo en su vivienda a una fuente de agua potable, energía eléctrica, alcantarillado y recolección de residuos sólidos.</span>"\
                "<br/><br/><b>Justificación y metodología:</b><br/>"\
                "<span>Se utilizan los datos disponibles por las empresas suministradoras de servicios privadas o municipales.</span>"\
                "<br/><br/><b>Formula:</b><br/>"\
                "<span>(No. viviendas con todos los servicios / No. total de viviendas)*100<br/>" 