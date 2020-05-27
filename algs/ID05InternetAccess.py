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
__date__ = '2020-01-14'
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
                       QgsProcessingParameterFile,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink)
from .ZProcesses import *
from .Zettings import *
from .ZHelpers import *
import numpy as np
import pandas as pd
import tempfile
import subprocess

#pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]

class ID05InternetAccess(QgsProcessingAlgorithm):
    """
    Cuantifica el número de hogares que pueden conectarse a internet usando un teléfono móvil
    o computador desde el hogar en relación al total de hogares.
    Formula: (Número de hogares con conexión a internet / Total de hogares)*100
    """

    BLOCKS = 'BLOCKS'
    DPA_MAN = 'DPA_MAN'
    CENSO_VIVIENDA = 'CENSO_VIVIENDA'
    # CENSO_POBLACION = 'CENSO_POBLACION'
    CENSO_HOGAR = 'CENSO_HOGAR'
    CELL_SIZE = 'CELL_SIZE'
    OUTPUT = 'OUTPUT'
    STUDY_AREA_GRID = 'STUDY_AREA_GRID'
    CURRENT_PATH = 'CURRENT_PATH'    

    def initAlgorithm(self, config):
        currentPath = getCurrentPath(self)
        self.CURRENT_PATH = currentPath        
        FULL_PATH = buildFullPathName(currentPath, nameWithOuputExtension(NAMES_INDEX['ID05'][1]))

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.BLOCKS,
                self.tr('Manzanas'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.DPA_MAN,
                self.tr('DPA Manzanas'),
                'dpa_manzan', 'BLOCKS'
            )
        )           


        self.addParameter(
            QgsProcessingParameterFile(
                self.CENSO_HOGAR,
                self.tr('Censo hogar'),
                extension='csv',
                defaultValue=""
            )
        )           

        self.addParameter(
            QgsProcessingParameterFile(
                self.CENSO_VIVIENDA,
                self.tr('Censo vivienda'),
                extension='csv',
                defaultValue=''
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


        # self.addParameter(
        #     QgsProcessingParameterNumber(
        #         self.NUMBER_HABITANTS,
        #         self.tr('Por cada número de habitantes'),
        #         QgsProcessingParameterNumber.Integer,
        #         100000, False, 1, 99999999
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
        steps = 0
        totalStpes = 17
        fieldDpaMan = params['DPA_MAN']
        # fieldHab = params['NUMBER_HABITANTS']

        feedback = QgsProcessingMultiStepFeedback(totalStpes, feedback)

        if not OPTIONAL_GRID_INPUT: params['CELL_SIZE'] = P_CELL_SIZE
        grid, isStudyArea = buildStudyArea(params['CELL_SIZE'], params['BLOCKS'],
                                         params['STUDY_AREA_GRID'],
                                         context, feedback)
        gridNeto = grid  


        steps = steps+1
        feedback.setCurrentStep(steps)


        # pathCsvPoblacion = params['CENSO_POBLACION']
        pathCsvHogar = params['CENSO_HOGAR']
        pathCsvVivienda = params['CENSO_VIVIENDA']

        fileH = pathCsvHogar
        colsH = ['I01', 'I02', 'I03', 'I04', 'I05', 'I06', 'I09', 'H01', 'H02', 'H03', 'H05', 'H07','H08', 'H09', 'H11','TP1']
        df = pd.read_csv(fileH, usecols=colsH)

        # fix codes 
        df['I01'] = df['I01'].astype(str)
        df['I02'] = df['I02'].astype(str)
        df['I03'] = df['I03'].astype(str)
        df['I04'] = df['I04'].astype(str)
        df['I05'] = df['I05'].astype(str)
        df['I06'] = df['I06'].astype(str)
        df['I09'] = df['I09'].astype(str)

        df.loc[df['I01'].str.len() < 2, 'I01'] = "0" + df['I01']
        df.loc[df['I02'].str.len() < 2, 'I02'] = "0" + df['I02']
        df.loc[df['I03'].str.len() < 2, 'I03'] = "0" + df['I03']
        df.loc[df['I04'].str.len() == 1, 'I04'] = "00" + df['I04']
        df.loc[df['I04'].str.len() == 2, 'I04'] = "0" + df['I04']
        df.loc[df['I05'].str.len() == 1, 'I05'] = "00" + df['I05']
        df.loc[df['I05'].str.len() == 2, 'I05'] = "0" + df['I05']
        df.loc[df['I06'].str.len() < 2, 'I06'] = "0" + df['I06']
        df.loc[df['I09'].str.len() == 1, 'I09'] = "00" + df['I09']
        df.loc[df['I09'].str.len() == 2, 'I09'] = "0" + df['I09']


        df['codv'] = df['I01'].astype(str) + df['I02'].astype(str) + df['I03'].astype(str) \
                  + df['I04'].astype(str) + df['I05'].astype(str) +  df['I06'].astype(str) \
                  + df['I09'].astype(str)


        # Calcular la disponibilidad de internet en el hogar.
        df['internet'] = None
        df.loc[df['H09'] == '1', 'internet'] = 1
        df.loc[df['H09'] == '2', 'internet'] = 0



        df['internet'] = df['internet'].astype(float)
        group = df.groupby('codv')['internet'].sum()
        df = group


        fileV = pathCsvVivienda
        colsV = ['I01', 'I02', 'I03', 'I04', 'I05', 'I06', 'I09', 
                 'I10', 
                 'V16', 'TOTPER'
                ]
        dfV = pd.read_csv(fileV, usecols=colsV)

        # fix codes 
        dfV['I01'] = dfV['I01'].astype(str)
        dfV['I02'] = dfV['I02'].astype(str)
        dfV['I03'] = dfV['I03'].astype(str)
        dfV['I04'] = dfV['I04'].astype(str)
        dfV['I05'] = dfV['I05'].astype(str)
        dfV['I06'] = dfV['I06'].astype(str)
        dfV['I09'] = dfV['I09'].astype(str)
        dfV['I10'] = dfV['I10'].astype(str)

        dfV.loc[dfV['I01'].str.len() < 2, 'I01'] = "0" + dfV['I01']
        dfV.loc[dfV['I02'].str.len() < 2, 'I02'] = "0" + dfV['I02']
        dfV.loc[dfV['I03'].str.len() < 2, 'I03'] = "0" + dfV['I03']
        dfV.loc[dfV['I04'].str.len() == 1, 'I04'] = "00" + dfV['I04']
        dfV.loc[dfV['I04'].str.len() == 2, 'I04'] = "0" + dfV['I04']
        dfV.loc[dfV['I05'].str.len() == 1, 'I05'] = "00" + dfV['I05']
        dfV.loc[dfV['I05'].str.len() == 2, 'I05'] = "0" + dfV['I05']
        dfV.loc[dfV['I06'].str.len() < 2, 'I06'] = "0" + dfV['I06']
        dfV.loc[dfV['I09'].str.len() == 1, 'I09'] = "00" + dfV['I09']
        dfV.loc[dfV['I09'].str.len() == 2, 'I09'] = "0" + dfV['I09']
        dfV.loc[dfV['I10'].str.len() < 2, 'I10'] = "0" + dfV['I10']


        dfV['codv'] = dfV['I01'].astype(str) + dfV['I02'].astype(str) + dfV['I03'].astype(str) \
                  + dfV['I04'].astype(str) + dfV['I05'].astype(str) +  dfV['I06'].astype(str) \
                  + dfV['I09'].astype(str)


        merge = None
        merge = pd.merge(dfV, df,  how='left', on='codv')
        merge.loc[merge['V16'] == ' ', 'V16'] = None

        df = merge
        df['codman'] = df['I01'].astype(str) + df['I02'].astype(str) + df['I03'].astype(str) \
                  + df['I04'].astype(str) + df['I05'].astype(str) + df['I06'].astype(str)


        df['V16'] = df['V16'].astype(float)
        aggOptions = {'codv' : 'count',
                      'internet':'sum', 
                       'V16' : 'sum', 
                      'codman' : 'first'
                     } 

        resManzanas = df.groupby('codman').agg(aggOptions)

        df = resManzanas
        df['acceso_inter'] = (df['internet'] / df['V16']) * 100                

        
        steps = steps+1
        feedback.setCurrentStep(steps)

        outputCsv = self.CURRENT_PATH+'/acceso_inter.csv'
        feedback.pushConsoleInfo(str(('acceso_inter en ' + outputCsv)))    
        df.to_csv(outputCsv, index=False)

        steps = steps+1
        feedback.setCurrentStep(steps)

        exitCsv = os.path.exists(outputCsv)
        if(exitCsv):
            print("El archivo CSV existe")
        else:
            print("No se encuentra CSV")

        CSV =  QgsVectorLayer(outputCsv, "csv", "ogr") 
        featuresCSV = CSV.getFeatures()
        # fields = layer.dataProvider().fields()
        field_names = [field.name() for field in CSV.fields()]       
        print(field_names)            

        steps = steps+1
        feedback.setCurrentStep(steps)

        steps = steps+1
        feedback.setCurrentStep(steps)
        result = joinByAttr2(params['BLOCKS'], fieldDpaMan,
                                outputCsv, 'codman',
                                [],
                                UNDISCARD_NONMATCHING,
                                '',
                                1,
                                context,
                                feedback)

        steps = steps+1
        feedback.setCurrentStep(steps)
        expressionNotNull = "acceso_inter IS NOT '' AND acceso_inter is NOT NULL"    
        notNull =   filterByExpression(result['OUTPUT'], expressionNotNull, context, feedback) 


        steps = steps+1
        feedback.setCurrentStep(steps)
        formulaDummy = 'acceso_inter * 1.0'
        result = calculateField(notNull['OUTPUT'], 
                                 'acceso_inter_n',
                                 formulaDummy,
                                 context,
                                 feedback)  


  # ----------------------CONVERTIR A NUMERICOS --------------------     
  
        steps = steps+1
        feedback.setCurrentStep(steps)
        formulaDummy = 'internet * 1.0'
        result = calculateField(result['OUTPUT'], 
                                 'internet_n',
                                 formulaDummy,
                                 context,
                                 feedback)  

        steps = steps+1
        feedback.setCurrentStep(steps)
        formulaDummy = 'V16 * 1.0'
        result = calculateField(result['OUTPUT'], 
                                 'V16_n',
                                 formulaDummy,
                                 context,
                                 feedback)          


       # ----------------------PROPORCIONES AREA--------------------------
       
        steps = steps+1
        feedback.setCurrentStep(steps)        
        blocks = calculateArea(result['OUTPUT'], 'area_bloc', context,
                               feedback)     

        steps = steps+1
        feedback.setCurrentStep(steps)
        segments = intersection(blocks['OUTPUT'], gridNeto['OUTPUT'],
                                ['internet_n','V16_n','area_bloc'],
                                ['id_grid','area_grid'],
                                context, feedback)        

        steps = steps+1
        feedback.setCurrentStep(steps)
        segmentsArea = calculateArea(segments['OUTPUT'],
                                     'area_seg',
                                     context, feedback)

        # -------------------------PROPORCIONES VALORES-------------------------

        steps = steps+1
        feedback.setCurrentStep(steps)
        formulaDummy = '(area_seg/area_bloc) * internet_n' 
        result = calculateField(segmentsArea['OUTPUT'], 'internet_n_seg',
                                               formulaDummy,
                                               context,
                                               feedback)     

        steps = steps+1
        feedback.setCurrentStep(steps)
        formulaDummy = '(area_seg/area_bloc) * V16_n' 
        result = calculateField(result['OUTPUT'], 'V16_n_seg',
                               formulaDummy,
                               context,
                               feedback)   


        steps = steps+1
        feedback.setCurrentStep(steps)
        result = makeSureInside(result['OUTPUT'],
                                context,
                                feedback)                                    

        #----------------------------------------------------------------------   

        steps = steps+1
        feedback.setCurrentStep(steps)
        result = joinByLocation(gridNeto['OUTPUT'],
                             result['OUTPUT'],
                             ['internet_n_seg','V16_n_seg'],                                   
                              [CONTIENE], [SUM],
                              UNDISCARD_NONMATCHING,
                              context,
                              feedback)  


        steps = steps+1
        feedback.setCurrentStep(steps)
        formulaDummy = '(internet_n_seg_sum/V16_n_seg_sum) * 100' 
        result = calculateField(result['OUTPUT'], NAMES_INDEX['ID05'][0],
                               formulaDummy,
                               context,
                               feedback, params['OUTPUT'])    



        # steps = steps+1
        # feedback.setCurrentStep(steps)
        # gridNeto = joinByLocation(gridNeto['OUTPUT'],
        #                      result['OUTPUT'],
        #                      ['acceso_inter_n'],                                   
        #                       [INTERSECTA], [MEDIA],
        #                       UNDISCARD_NONMATCHING,
        #                       context,
        #                       feedback)         
 

        # fieldsMapping = [
        #     {'expression': '"id_grid"', 'length': 10, 'name': 'id_grid', 'precision': 0, 'type': 4}, 
        #     {'expression': '"area_grid"', 'length': 16, 'name': 'area_grid', 'precision': 3, 'type': 6}, 
        #     {'expression': '"acceso_inter_n_mean"', 'length': 20, 'name': NAMES_INDEX['ID05'][0], 'precision': 2, 'type': 6}
        # ]      
        
        # steps = steps+1
        # feedback.setCurrentStep(steps)
        # result = refactorFields(fieldsMapping, gridNeto['OUTPUT'], 
        #                         context,
        #                         feedback, params['OUTPUT'])                                                                

        return result
          
    def icon(self):
        return QIcon(os.path.join(pluginPath, 'wifi.png'))

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'D05 Acceso a internet'

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
        return ID05InternetAccess()

    def shortHelpString(self):
        return  "<b>Descripción:</b><br/>"\
                "<span>Cuantifica el número de hogares que pueden conectarse a internet usando un teléfono móvil o computador desde el hogar en relación al total de hogares.</span>"\
                "<br/><br/><b>Justificación y metodología:</b><br/>"\
                "<span></span>"\
                "<br/><br/><b>Formula:</b><br/>"\
                "<span>(Número de hogares con conexión a internet / Total de hogares)*100</span><br/>"