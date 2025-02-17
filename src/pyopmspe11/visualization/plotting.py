# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: MIT

""""
Script to plot the results
"""

import argparse
import os
import math as mt
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

font = {"family": "normal", "weight": "normal", "size": 15}
matplotlib.rc("font", **font)
plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "monospace",
        "legend.columnspacing": 0.9,
        "legend.handlelength": 3.5,
        "legend.fontsize": 15,
        "lines.linewidth": 4,
        "axes.titlesize": 15,
        "axes.grid": True,
        "figure.figsize": (10, 5),
    }
)

SECONDS_IN_YEAR = 31536000.0


def main():
    """Postprocessing"""
    parser = argparse.ArgumentParser(description="Main script to plot the results")
    parser.add_argument(
        "-p",
        "--folder",
        default="output",
        help="The folder to the opm simulations.",
    )
    parser.add_argument(
        "-c",
        "--compare",
        default="",
        help="Generate a common plot for the current folders.",
    )
    parser.add_argument(
        "-d",
        "--deck",
        default="spe11b",
        help="The simulated spe case.",
    )
    parser.add_argument(
        "-t",
        "--time",
        default="24",
        help="Time interval for the spatial maps (spe11b/c [y]; spe11a [h]) ('24' by default).",
    )
    parser.add_argument(
        "-g",
        "--generate",
        default="sparse",
        help="Plot only the 'dense', 'sparse', 'performance', 'dense_performance', "
        "'performance_sparse', 'dense_sparse', or 'all'",
    )
    cmdargs = vars(parser.parse_known_args()[0])
    dic = {"folders": [cmdargs["folder"].strip()]}
    dic["case"] = cmdargs["deck"].strip()
    dic["generate"] = cmdargs["generate"].strip()
    dic["spatial_t"] = float(cmdargs["time"].strip())
    dic["compare"] = cmdargs["compare"]  # No empty, then the create compare folder
    dic["exe"] = os.getcwd()  # Path to the folder of the configuration file
    plot_results(dic)


def plot_results(dic):
    """Make the figures"""
    dic["colors"] = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
        "r",
    ]
    dic["linestyle"] = [
        "--",
        (0, (1, 1)),
        "-.",
        (0, (1, 10)),
        (0, (1, 1)),
        (5, (10, 3)),
        (0, (5, 10)),
        (0, (5, 5)),
        (0, (5, 1)),
        (0, (3, 10, 1, 10)),
        (0, (3, 5, 1, 5)),
        (0, (3, 1, 1, 1)),
        (0, (3, 5, 1, 5, 1, 5)),
        (0, (3, 10, 1, 10, 1, 10)),
        (0, (3, 1, 1, 1, 1, 1)),
        (0, ()),
        "-",
    ]
    dic["props"] = {"boxstyle": "round", "facecolor": "wheat", "alpha": 0.1}
    if dic["compare"]:
        dic["case"] = dic["compare"]
        dic["where"] = "compare/"
        dic["folders"] = sorted(
            [name for name in os.listdir(".") if os.path.isdir(name)]
        )
        if "compare" not in dic["folders"]:
            os.system(f"mkdir {dic['exe']}/compare")
        else:
            os.system(f"rm -rf {dic['exe']}/compare")
            os.system(f"mkdir {dic['exe']}/compare")
            dic["folders"].remove("compare")
    else:
        dic["where"] = f"{dic['exe']}/{dic['folders'][0]}/figures"
    if dic["case"] == "spe11a":
        dic["tlabel"] = "h"
        dic["dims"] = 2
        dic["tscale"] = 3600.0
    else:
        dic["tlabel"] = "y"
        dic["dims"] = 2
        dic["tscale"] = SECONDS_IN_YEAR
    if dic["case"] == "spe11c":
        dic["dims"] = 3
    if dic["generate"] in [
        "all",
        "performance",
        "dense_performance",
        "performance_sparse",
    ]:
        performance(dic)
    if dic["generate"] in ["all", "sparse", "dense_sparse", "performance_sparse"]:
        sparse_data(dic)
    if dic["compare"]:
        return
    plt.rcParams.update({"axes.grid": False})
    if dic["generate"] in ["all", "dense", "dense_performance", "dense_sparse"]:
        dense_data(dic)


def performance(dic):
    """time solver plots"""
    csv = np.genfromtxt(
        f"{dic['exe']}/{dic['folders'][0]}/data/{dic['case']}_performance_time_series.csv",
        delimiter=",",
        skip_header=1,
    )
    times = [csv[i][0] for i in range(csv.shape[0])]
    dic["fig"] = plt.figure(figsize=(40, 75))
    plots = [
        "tstep",
        "fsteps",
        "mass",
        "dof",
        "nliter",
        "nres",
        "liniter",
        "runtime",
        "tlinsol",
    ]
    ylabels = ["s", "\\#", "kg", "\\#", "\\#", "\\#", "\\#", "s", "s"]
    for k, (plot, ylabel) in enumerate(zip(plots, ylabels)):
        axis = dic["fig"].add_subplot(9, 5, k + 1)
        for nfol, fol in enumerate(dic["folders"]):
            csv = np.genfromtxt(
                f"{dic['exe']}/{fol}/data/{dic['case']}_performance_time_series.csv",
                delimiter=",",
                skip_header=1,
            )
            labels = [
                f"sum={sum((csv[i][1] for i in range(csv.shape[0]))):.3e}",
                f"sum={sum((csv[i][2] for i in range(csv.shape[0]))):.3e}",
                f"max={max((csv[i][3] for i in range(csv.shape[0]))):.3e}",
                f"max={csv[-1][4]:.3e}",
                f"sum={sum((csv[i][5] for i in range(csv.shape[0]))):.3e}",
                f"sum={sum((csv[i][6] for i in range(csv.shape[0]))):.3e}",
                f"sum={sum((csv[i][7] for i in range(csv.shape[0]))):.3e}",
                f"sum={sum((csv[i][8] for i in range(csv.shape[0]))):.3e}",
                f"sum={sum((csv[i][9] for i in range(csv.shape[0]))):.3e}",
            ]
            times = [csv[i][0] / dic["tscale"] for i in range(csv.shape[0])]
            labels[k] += f" ({fol})"
            axis.plot(
                times,
                [csv[i][k + 1] for i in range(csv.shape[0])],
                lw=2,
                color=dic["colors"][nfol],
                label=labels[k],
            )
            axis.set_title(plot + f", {dic['case']}")
            axis.set_ylabel(ylabel)
            axis.set_xlabel(f"Time [{dic['tlabel']}]")
            axis.legend()
    dic["fig"].savefig(
        f"{dic['where']}/{dic['case']}_performance.png", bbox_inches="tight"
    )


def sparse_data(dic):
    """time plots"""
    dic["fig"] = plt.figure(figsize=(25, 40))
    plots = ["sensors", "boxA", "boxB", "boxC", "facie 1"]
    ylabels = ["Presure [Pa]", "Mass [kg]", "Mass [kg]", "Area [m$^2$]", "Mass [kg]"]
    labels = [
        ["p1", "p2"],
        ["mobA", "immA", "dissA", "sealA"],
        ["mobB", "immB", "dissB", "sealB"],
        ["MC"],
        ["sealTot"],
    ]
    dic["nfigs"] = 5
    if dic["case"] != "spe11a":
        plots += ["boundaries"]
        ylabels += ["Mass [kg]"]
        labels.append(["boundTot"])
        dic["nfigs"] += 1
    for k, (plot, ylabel) in enumerate(zip(plots, ylabels)):
        axis = dic["fig"].add_subplot(dic["nfigs"], 3, k + 1)
        for nfol, fol in enumerate(dic["folders"]):
            ncol = sum(len(labels[i]) for i in range(k)) + 1
            axis.text(
                0.7,
                0.15 + nfol * 0.05,
                fol,
                transform=axis.transAxes,
                verticalalignment="top",
                bbox=dic["props"],
                color=dic["colors"][nfol],
            )
            csv = np.genfromtxt(
                f"{dic['exe']}/{fol}/data/{dic['case']}_time_series.csv",
                delimiter=",",
                skip_header=1,
            )
            times = [csv[i][0] / dic["tscale"] for i in range(csv.shape[0])]
            for j, label in enumerate(labels[k]):
                if nfol == 0:
                    axis.plot(
                        times,
                        [csv[i][ncol] for i in range(csv.shape[0])],
                        label=label,
                        color="k",
                        linestyle=dic["linestyle"][-1 + j],
                    )
                axis.plot(
                    times,
                    [csv[i][ncol] for i in range(csv.shape[0])],
                    color=dic["colors"][nfol],
                    linestyle=dic["linestyle"][-1 + j],
                )
                ncol += 1
        axis.set_title(plot + f", {dic['case']}")
        axis.set_ylabel(ylabel)
        axis.set_xlabel(f"Time [{dic['tlabel']}]")
        axis.legend()
    dic["fig"].savefig(
        f"{dic['where']}/{dic['case']}_sparse_data.png", bbox_inches="tight"
    )


def dense_data(dic):
    """2D spatial maps"""
    dic["quantities"] = ["pressure", "sgas", "xco2", "xh20", "gden", "wden", "tco2"]
    dic["units"] = ["[Pa]", "[-]", "[-]", "[-]", r"[kg/m$^3$]", r"[kg/m$^3$]", "[kg]"]
    if dic["case"] != "spe11a":
        dic["quantities"] += ["temp"]
        dic["units"] += ["C"]
    dic["files"] = [
        f
        for f in os.listdir(f"{dic['exe']}/{dic['folders'][0]}/data")
        if f.endswith(f"{dic['tlabel']}.csv")
    ]
    dic["times"] = np.array([int(file[19:-5]) for file in dic["files"]])
    dic["sort_ind"] = np.argsort(dic["times"])
    dic["files"] = [dic["files"][i] for i in dic["sort_ind"]]
    dic["times"] = [dic["times"][i] for i in dic["sort_ind"]]
    dic["tmaps"] = [
        i * round(dic["spatial_t"])
        for i in range(1, round(dic["times"][-1] / (dic["spatial_t"])) + 1)
    ]
    csv = np.genfromtxt(
        f"{dic['exe']}/{dic['folders'][0]}/data/{dic['files'][0]}",
        delimiter=",",
        skip_header=1,
    )
    dic["length"] = csv[-1][0] + csv[0][0]
    dic["width"] = csv[-1][dic["dims"] - 2] + csv[0][dic["dims"] - 2]
    dic["height"] = csv[-1][dic["dims"] - 1] + csv[0][dic["dims"] - 1]
    dic["xmx"] = np.linspace(
        0, dic["length"], round(dic["length"] / (2.0 * csv[0][0])) + 1
    )
    dic["ymy"] = np.linspace(
        0, dic["width"], round(dic["width"] / (2.0 * csv[0][dic["dims"] - 2])) + 1
    )
    dic["zmz"] = np.linspace(
        0, dic["height"], round(dic["height"] / (2.0 * csv[0][dic["dims"] - 1])) + 1
    )
    dic["xmsh"], dic["zmsh"] = np.meshgrid(dic["xmx"], dic["zmz"][::-1])
    for k, quantity in enumerate(dic["quantities"]):
        if dic["case"] != "spe11a":
            dic["fig"] = plt.figure(figsize=(38, 3 * len(dic["tmaps"])))
        else:
            dic["fig"] = plt.figure(figsize=(34, 5 * len(dic["tmaps"])))
        dic["plot"] = []
        csv = np.genfromtxt(
            f"{dic['exe']}/{dic['folders'][0]}/data/{dic['files'][0]}",
            delimiter=",",
            skip_header=1,
        )
        quan = np.array([csv[i][dic["dims"] + k] for i in range(csv.shape[0])])
        dic["minc"] = quan[~np.isnan(quan)].min()
        dic["maxc"] = quan[~np.isnan(quan)].max()
        for tmap in dic["tmaps"]:
            csv = np.genfromtxt(
                f"{dic['exe']}/{dic['folders'][0]}/data/{dic['case']}_spatial_map_"
                + f"{tmap}{dic['tlabel']}.csv",
                delimiter=",",
                skip_header=1,
            )
            quan = np.array([csv[i][dic["dims"] + k] for i in range(csv.shape[0])])
            dic["minc"] = min(dic["minc"], quan[quan >= 0].min())
            dic["maxc"] = max(dic["maxc"], quan[quan >= 0].max())
            dic["plot"].append(np.zeros([len(dic["zmz"]) - 1, len(dic["xmx"]) - 1]))
            for i in np.arange(0, len(dic["zmz"]) - 1):
                if dic["case"] != "spe11c":
                    dic["plot"][-1][-1 - i, :] = quan[
                        i * (len(dic["xmx"]) - 1) : (i + 1) * (len(dic["xmx"]) - 1)
                    ]
                else:
                    dic["plot"][-1][-1 - i, :] = quan[
                        (i * (len(dic["ymy"]) - 1) * (len(dic["xmx"]) - 1))
                        + mt.floor((len(dic["ymy"]) - 1) / 2)
                        * (len(dic["xmx"]) - 1) : (
                            (len(dic["xmx"]) - 1)
                            + i * (len(dic["ymy"]) - 1) * (len(dic["xmx"]) - 1)
                            + mt.floor((len(dic["ymy"]) - 1) / 2)
                            * (len(dic["xmx"]) - 1)
                        )
                    ]
        for j, time in enumerate(dic["tmaps"]):
            axis = dic["fig"].add_subplot(len(dic["tmaps"]), 3, j + 1)
            imag = axis.pcolormesh(
                dic["xmsh"],
                dic["zmsh"],
                dic["plot"][j],
                shading="flat",
                cmap="jet",
            )
            axis.set_title(
                f"{time}{dic['tlabel']}, {quantity} "
                + dic["units"][k]
                + f", {dic['case']} ({dic['folders'][0]})"
            )
            axis.axis("scaled")
            axis.set_xlabel("x [m]")
            axis.set_ylabel("z [m]")
            divider = make_axes_locatable(axis)
            vect = np.linspace(
                dic["minc"],
                dic["maxc"],
                5,
                endpoint=True,
            )
            dic["fig"].colorbar(
                imag,
                cax=divider.append_axes("right", size="5%", pad=0.05),
                orientation="vertical",
                ticks=vect,
                format=lambda x, _: f"{x:.2e}",
            )
            imag.set_clim(
                dic["minc"],
                dic["maxc"],
            )
        dic["fig"].savefig(
            f"{dic['where']}/{dic['case']}_{quantity}_2Dmaps.png", bbox_inches="tight"
        )
        plt.close()


if __name__ == "__main__":
    main()
