# -*- coding: utf-8 -*-

"""
***************************************************************************
    dinftranslimaccum2.py
    ---------------------
    Date                 : October 2012
    Copyright            : (C) 2012 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""


__author__ = 'Alexander Bruy'
__date__ = 'October 2012'
__copyright__ = '(C) 2012, Alexander Bruy'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os

from PyQt4.QtGui import *

from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.core.SextanteLog import SextanteLog
from sextante.core.SextanteUtils import SextanteUtils
from sextante.core.SextanteConfig import SextanteConfig
from sextante.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException

from sextante.parameters.ParameterRaster import ParameterRaster
from sextante.parameters.ParameterVector import ParameterVector
from sextante.parameters.ParameterBoolean import ParameterBoolean

from sextante.outputs.OutputRaster import OutputRaster

from sextante.taudem.TauDEMUtils import TauDEMUtils

class DinfTransLimAccum2(GeoAlgorithm):
    DINF_FLOW_DIR_GRID = "DINF_FLOW_DIR_GRID"
    SUPPLY_GRID = "SUPPLY_GRID"
    CAPACITY_GRID = "CAPACITY_GRID"
    IN_CONCENTR_GRID = "IN_CONCENTR_GRID"
    OUTLETS_SHAPE = "OUTLETS_SHAPE"
    EDGE_CONTAM = "EDGE_CONTAM"

    TRANSP_LIM_ACCUM_GRID = "TRANSP_LIM_ACCUM_GRID"
    DEPOSITION_GRID = "DEPOSITION_GRID"
    OUT_CONCENTR_GRID = "OUT_CONCENTR_GRID"

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/../images/taudem.png")

    def defineCharacteristics(self):
        self.name = "D-Infinity Transport Limited Accumulation - 2"
        self.cmdName = "dinftranslimaccum"
        self.group = "Specialized Grid Analysis tools"

        self.addParameter(ParameterRaster(self.DINF_FLOW_DIR_GRID, "D-Infinity Flow Direction Grid", False))
        self.addParameter(ParameterRaster(self.SUPPLY_GRID, "Supply Grid", False))
        self.addParameter(ParameterRaster(self.CAPACITY_GRID, "Transport Capacity Grid", False))
        self.addParameter(ParameterRaster(self.IN_CONCENTR_GRID, "Input Concentration Grid", False))
        self.addParameter(ParameterVector(self.OUTLETS_SHAPE, "Outlets Shapefile", ParameterVector.VECTOR_TYPE_POINT, True))
        self.addParameter(ParameterBoolean(self.EDGE_CONTAM, "Check for edge contamination", True))

        self.addOutput(OutputRaster(self.TRANSP_LIM_ACCUM_GRID, "Transport Limited Accumulation Grid"))
        self.addOutput(OutputRaster(self.DEPOSITION_GRID, "Deposition Grid"))
        self.addOutput(OutputRaster(self.OUT_CONCENTR_GRID, "Output Concentration Grid"))

    def processAlgorithm(self, progress):
        commands = []
        commands.append(os.path.join(TauDEMUtils.mpiexecPath(), "mpiexec"))

        processNum = SextanteConfig.getSetting(TauDEMUtils.MPI_PROCESSES)
        if processNum <= 0:
          raise GeoAlgorithmExecutionException("Wrong number of MPI processes used.\nPlease set correct number before running TauDEM algorithms.")

        commands.append("-n")
        commands.append(str(processNum))
        commands.append(os.path.join(TauDEMUtils.taudemPath(), self.cmdName))
        commands.append("-ang")
        commands.append(self.getParameterValue(self.DINF_FLOW_DIR_GRID))
        commands.append("-tsup")
        commands.append(self.getParameterValue(self.SUPPLY_GRID))
        commands.append("-tc")
        commands.append(self.getParameterValue(self.CAPACITY_GRID))
        commands.append("-cs")
        commands.append(self.getParameterValue(self.IN_CONCENTR_GRID))
        param = self.getParameterValue(self.OUTLETS_SHAPE)
        if param is not None:
          commands.append("-o")
          commands.append(param)
        if str(self.getParameterValue(self.EDGE_CONTAM)).lower() == "false":
            commands.append("-nc")

        commands.append("-tla")
        commands.append(self.getOutputValue(self.TRANSP_LIM_ACCUM_GRID))
        commands.append("-tdep")
        commands.append(self.getOutputValue(self.DEPOSITION_GRID))
        commands.append("-ctpt")
        commands.append(self.getOutputValue(self.OUT_CONCENTR_GRID))

        loglines = []
        loglines.append("TauDEM execution command")
        for line in commands:
            loglines.append(line)
        SextanteLog.addToLog(SextanteLog.LOG_INFO, loglines)

        TauDEMUtils.executeTauDEM(commands, progress)

    #def helpFile(self):
    #    return os.path.join(os.path.dirname(__file__), "help", self.cmdName + ".html")
