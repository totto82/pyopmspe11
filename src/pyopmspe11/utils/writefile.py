# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: MIT

"""
Utiliy functions for necessary files and variables to run OPM Flow.
"""

import os
import subprocess
from mako.template import Template


def initial(dic):
    """
    Function to run Flow to generate output files used for e.g., find cell coordinates

    Args:
        dic (dict): Global dictionary with required parameters

    """
    var = {"dic": dic}
    mytemplate = Template(filename=f"{dic['pat']}/templates/common/grid_initial.mako")
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/deck/GRID.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    mytemplate = Template(filename=f"{dic['pat']}/templates/common/deck_initial.mako")
    var = {"dic": dic}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/deck/INITIAL.DATA", "w", encoding="utf8"
    ) as file:
        file.write(filledtemplate)


def write_keywords(dic):
    """
    Function to write some of the used keywords and values

    Args:
        dic (dict): Global dictionary with required parameters

    """
    if dic["spe11"] == "spe11a":
        if dic["grid"] == "tensor":
            keywords = ["satnum", "fipnum", "poro", "permx", "dx", "dz"]
            dic["dx"] = list(map(str, list((dic["xmx"][1:] - dic["xmx"][:-1]))))
            d_z = list(map(str, list((dic["zmz"][1:] - dic["zmz"][:-1]))))
            dic["dz"] = [d_z[0]] * dic["noCells"][0]
            for i in range(dic["noCells"][2] - 1):
                dic["dx"].extend(dic["dx"][-dic["noCells"][0] :])
                dic["dz"] += [d_z[i + 1]] * dic["noCells"][0]
        else:
            keywords = ["satnum", "fipnum", "poro", "permx"]
    elif dic["spe11"] == "spe11b":
        dic["dx"] = list(map(str, list((dic["xmx"][1:] - dic["xmx"][:-1]))))
        if dic["grid"] == "tensor":
            keywords = ["satnum", "fipnum", "poro", "permx", "thconr", "dx", "dz"]
            d_z = list(map(str, list((dic["zmz"][1:] - dic["zmz"][:-1]))))
            dic["dz"] = [d_z[0]] * dic["noCells"][0]
            for i in range(dic["noCells"][2] - 1):
                dic["dx"].extend(dic["dx"][-dic["noCells"][0] :])
                dic["dz"] += [d_z[i + 1]] * dic["noCells"][0]
        else:
            keywords = ["satnum", "fipnum", "poro", "permx", "thconr", "dx"]
            for _ in range(dic["noCells"][2] - 1):
                dic["dx"].extend(dic["dx"][-dic["noCells"][0] :])
    else:
        keywords = ["satnum", "fipnum", "poro", "permx", "thconr"]
    for names in keywords:
        dic[f"{names}"].insert(0, f"{names.upper()}")
        dic[f"{names}"].append("/")
        with open(
            f"{dic['exe']}/{dic['fol']}/deck/{names.upper()}.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("\n".join(dic[f"{names}"]))


def opm_files(dic):
    """
    Function to write opm-related files by running mako templates

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    write_keywords(dic)
    mytemplate = Template(filename=f"{dic['pat']}/templates/co2/{dic['spe11']}.mako")
    var = {"dic": dic}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/deck/{dic['fol'].upper()}.DATA",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    if dic["spe11"] == "spe11c":
        if dic["grid"] == "corner-point":
            mytemplate = Template(
                filename=f"{dic['pat']}/templates/common/grid_corner.mako"
            )
        else:
            mytemplate = Template(
                filename=f"{dic['pat']}/templates/common/grid_tensor.mako"
            )
        filledtemplate = mytemplate.render(**var)
        with open(
            f"{dic['exe']}/{dic['fol']}/deck/GRID.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write(filledtemplate)
    mytemplate = Template(
        filename=f"{dic['pat']}/templates/common/saturation_functions.mako"
    )
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/deck/saturation_functions.py",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    os.system(f"chmod u+x {dic['exe']}/{dic['fol']}/deck/saturation_functions.py")
    prosc = subprocess.run(
        ["python3", f"{dic['exe']}/{dic['fol']}/deck/saturation_functions.py"],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")
    os.system(f"rm -rf {dic['exe']}/{dic['fol']}/deck/saturation_functions.py")
