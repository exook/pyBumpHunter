# Here we test pyBumpHunter.
# The result can be compared to what can be obtained with the original C++ version.
# We will use histograms ranging between 0 and 20 with 60 even bins.

import matplotlib

matplotlib.use("Agg")
from datetime import datetime  # # Used to compute the execution time

import matplotlib.pyplot as plt
import uproot  # # Used to read data from a root file

import pyBumpHunter as BH

import sys

def bumpHunt(year):
    # Open the file
    with uproot.open("./data.root") as file:
        # Background
        bkg = file["bkg"].arrays(library="np")["bkg"]

        # Data
        data = file["data"].arrays(library="np")["data"]

        # Signal
        sig = file["sig"].arrays(library="np")["sig"]
        
    with uproot.open(f"../../data/bat/merged/{year}/{year}_OnOffCalib.root") as file:
        calib_hist = file["hpx"].to_numpy()
        
    # Position of the bump in the data
    Lth = 5.5

    # Range for the histograms (same that the one used with C++ BumpHunter)
    rang = [0, 2000]
    bins = [92,107,122,138,154,171,188,206,224,243,262,282,302,323,344,365,387,410,433,457,481,506,531,556,582,608,635,662,690,719,748,778,808,839,871,903,936,970,1004,1039,1075,1111,1148,1186,1225,1264,1304,1345,1387,1429,1472,1516,1561,1607,1654,1701,1749,1798,1848,1899,1951,2004,2058,2113,2169,2226,2284,2343,2403,2464,2526,2590,2655,2721,2788,2856,2926,2997,3069,3142,3217,3293,3371,3450,3530,3612,3695,3780,3866,3954,4043,4134,4227,4321,4417,4515,4614,4715,4818,4923,5030]

    # Plot the 2 distributions
    F = plt.figure(figsize=(12, 8))
    bkg_hist=plt.hist(
        (bkg),
        bins=bins,
        histtype="step",
        label=("Background"),
        linewidth=2,
    )
    x=[]
    bin_edges=bins
    for i in range(1,len(bin_edges)):
        bin_center = bin_edges[i-1]+((bin_edges[i]-bin_edges[i-1])/2)
        x.append(bin_center)
    bkg_x = x
    bkg_y = bkg_hist[0]
    data_x = x
    data_y = bkg_hist[0]*calib_hist[0]
    data_hist=plt.plot(
        data_x,data_y,
        label="Bkg * Calib",
        linestyle='none',
        markerSize=2,
        marker="o",
        color="red",
    )
    plt.legend(fontsize='xx-large',title=year)
    plt.xticks(fontsize='xx-large')
    plt.yticks(fontsize='xx-large')
    plt.savefig(f"results/1D/{year}/hist.png", bbox_inches="tight")
    plt.close(F)
    

    # Create a BumpHunter1D class instance
    hunter = BH.BumpHunter1D(
        rang=rang,
        width_min=2,
        width_max=6,
        width_step=1,
        scan_step=1,
        npe=10000,
        nworker=1,
        seed=666,
    )

    # Call the bump_scan method
    print("####bump_scan call####")
    begin = datetime.now()
    data = [data_x,data_y]
    bkg = [bkg_x,bkg_y]
    hunter.bump_scan(data,bkg)
    end = datetime.now()
    print(f"time={end - begin}")
    print("")

    # Print bump
    print(hunter.bump_info(data))
    print(f"   mean (true) = {Lth}")
    print("")

    # Get and save tomography plot
    hunter.plot_tomography(data, filename=f"results/1D/{year}/tomography.png")

    # Get and save bump plot
    hunter.plot_bump(data, bkg, filename=f"results/1D/{year}/bump.png",label=", "+year)

## Get and save statistics plot
#hunter.plot_stat(show_Pval=True, filename="results/1D/BH_statistics.png")

#print("")

## We have to set additionnal parameters specific to the signal injection.
## All the parameters defined previously are kept.
#hunter.sigma_limit = 5
#hunter.str_min = -1  # if str_scale='log', the real starting value is 10**str_min
#hunter.str_scale = "log"
#hunter.signal_exp = 150  # Correspond the the real number of signal events generated when making the data

#print("####singal_inject call####")
#begin = datetime.now()
#hunter.signal_inject(sig, bkg, is_hist=False)
#end = datetime.now()
#print(f"time={end - begin}")
#print("")

## Get and save the injection plot
#hunter.plot_inject(
#    filename=("results/1D/SignalInject.png", "results/1D/SignalInject_log.png")
#)

def main():
    years = ["data15","data16","data17","data18"]
    for year in years:
        bumpHunt(year)

if __name__ == "__main__":
    main()
