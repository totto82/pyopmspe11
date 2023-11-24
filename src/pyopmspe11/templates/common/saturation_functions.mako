# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: MIT
#!/usr/bin/env python

""""
Script to write the saturation functions
"""

import math
import numpy as np


def s_w_points(npoints):
    """
    Points to evaluate the saturation functions

    """
    return ${dic['s_w'].strip()}


def krw(s_w, swi):
    """
    Wetting relative permeability

    """
    return ${dic['krw'].strip()}


def krn(s_w, sni):
    """
    CO2 relative permeability

    """
    return ${dic['krn'].strip()}


def pcap(s_w, swi, pen, penmax):
    """
    Capillary pressure

    """
    return ${dic['pcap'].strip()}


def safu_evaluation():
    """
    Saturation function assignation

    """

    # Properties: swi, sni, pen, penmax, npoints
    safu = [[0.0] * 5 for _ in range(${len(dic['safu'])})]
    % for i, _ in enumerate(dic['safu']):
    % for j, _ in enumerate(dic['safu'][i]):
    safu[${i}][${j}] = ${dic['safu'][i][j]}
    % endfor
    % endfor

    with open(
        "${dic['exe']}/${dic['fol']}/deck/TABLES.INC",
        "w",
        encoding="utf8",
    ) as file:
        % if dic["co2store"] == "gaswater":
        file.write("SGWFN\n")
        % else:
        file.write("SGOF\n")
        % endif
        for _, para in enumerate(safu):
            s_n = 1.0 - s_w_points(para[4])
            for value in s_n:
                if 1.0 - value > para[0]:
                    file.write(
                        f"{value:E} {krn(1.0 - value, para[1]) :E}"
                        f" {krw(1.0 - value, para[0]) :E}"
                        f" {pcap(1.0 - value, para[0], para[2], para[3])/1.e5 : E} \n"
                    )
                else:
                    file.write(
                        f"{value:E} {krn(1.0 - value, para[1]) :E}"
                        f" {krw(1.0 - value, para[0]) :E}"
                        f" {para[3]/1.e5 : E} \n"
                    )
            file.write("/\n")


if __name__ == "__main__":
    safu_evaluation()
