############################################################################
#
#    QuadcopeRPI- SW for controlling a quadcopter by RPI
#
#    Copyright (C) 2014 Oscar Ferrato (solenero tech)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#    Contact me at:
#    solenero.tech@gmail.com
#    solenerotech.wordpress.com
##############################################################################

import logging


def setupLogger(name, debuglevel, file_name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    #formatter = logging.Formatter(
    #    "%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")
    formatter = logging.Formatter('%(asctime) -25s - %(name) -15s - %(levelname) -10s - %(message)s')
    formatterDisplay = logging.Formatter('%(asctime)-8s|%(name)-12s|%(levelname)-6s|%(message)-s', '%H:%M:%S')
    # Alternative formatting available on python 3.2+:
    # formatter = logging.Formatter(
    #     "{asctime} {threadName:>11} {levelname} {message}", style='{')

    # Log to file
    filehandler = logging.FileHandler(file_name, 'w')

    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)

    # Log to stdout too
    streamhandler = logging.StreamHandler()

    streamhandler.setFormatter(formatterDisplay)
    logger.addHandler(streamhandler)

    if debuglevel:
        filehandler.setLevel(logging.DEBUG)
        streamhandler.setLevel(logging.DEBUG)
    else:
        filehandler.setLevel(logging.INFO)
        streamhandler.setLevel(logging.INFO)

    return logger

