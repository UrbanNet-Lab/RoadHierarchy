import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.optimize import curve_fit
from scipy.stats import linregress, t
from sklearn.metrics import r2_score
from matplotlib.font_manager import FontProperties

# ---------- Utility Functions (unchanged) ---------- #

def current_time_version():
    now = datetime.now()
    year, month, day = now.year, now.month, now.day
    hours = str(now.hour).zfill(2)
    minutes = str(now.minute).zfill(2)
    seconds = str(now.second).zfill(2)
    return f"{year}-{month}-{day} {hours}-{minutes}-{seconds}"

def line_func(x, a, b):
    return b * x + a

def log_avg(x, y, num):
    min_x, max_x = min(x), max(x)
    bins = np.logspace(np.log10(min_x), np.log10(max_x), num)
    bins_all = {bins[i]: [] for i in range(len(bins) - 1)}

    for i in range(len(x)):
        added = False
        for j in range(1, len(bins)):
            if x[i] <= bins[j]:
                bins_all[bins[j - 1]].append(y[i])
                added = True
                break
        if not added:
            bins_all[bins[-2]].append(y[i])

    x_avg, y_avg = [], []
    for i in range(len(bins) - 1):
        value = bins_all[bins[i]]
        if value:
            midpoint = (bins[i] + bins[i + 1]) / 2
            y_avg.append(np.mean(value))
            x_avg.append(midpoint)
    return x_avg, y_avg

# ---------- Core Fitting and Plotting Function ---------- #

def logbinning_fitPower(x, y, num_bins, ax, label, x_loc, y_loc_up, y_loc_down,
                        scatter_color, bin_color, bin_fit=False, confidence_band=False, word_up=True):
    """
    Perform log-binning and power-law fitting on data, and plot results.

    Parameters:
        x, y             : Input data
        num_bins         : Number of bins for log-binning
        ax               : Matplotlib axis for plotting
        label            : Title/text inside plot
        x_loc, y_loc_up  : Text position for plot annotation
        scatter_color    : Color of binned points
        bin_color        : Color of raw scatter points
        bin_fit          : Whether to fit on binned values
        confidence_band  : Show 95% CI of fit
        word_up          : Place annotation at top or bottom
    """
    if len(x) <= 5:
        return

    x, y = np.array(x), np.array(y)
    slope, intercept, *_ = linregress(np.log10(x), np.log10(y))
    y_fit = slope * np.log10(x) + intercept
    residuals = np.log10(y) - y_fit

    x_bin, y_bin = log_avg(x, y, num_bins)
    x_bin, y_bin = np.array(x_bin), np.array(y_bin)

    x_fit = np.log10(x_bin if bin_fit else x)
    y_fit = np.log10(y_bin if bin_fit else y)

    popt, pcov = curve_fit(line_func, x_fit, y_fit)
    fit_y = line_func(x_fit, *popt)
    r2 = r2_score(y_fit, fit_y)

    dof = max(0, len(x_fit) - len(popt))
    t_value = t.ppf(0.975, dof)
    se_b = np.sqrt(np.diag(pcov))[1]
    ci_b = t_value * se_b

    ci = t_value * np.sqrt(
        np.diag(pcov)[0]**2 +
        (np.diag(pcov)[1]**2) * x_fit**2 +
        2 * pcov[0, 1] * x_fit
    )

    ax.loglog()
    ax.scatter(x, y, s=7, c=bin_color, alpha=0.8, edgecolors='none', label='Raw data')
    ax.scatter(10**x_fit, 10**y_fit, s=24, facecolors='none', edgecolors=scatter_color, alpha=1, label='Binned avg')
    ax.plot(10**x_fit, 10**fit_y, 'r-', linewidth=1, label='Fit')

    if confidence_band:
        ax.fill_between(10**x_fit, 10**(fit_y - ci), 10**(fit_y + ci), color='lightgray', alpha=0.5)

    ax.tick_params(labelsize=17)
    ax.text(0.05, 0.95, label, fontsize=17, transform=ax.transAxes, verticalalignment='top')

    annotation_text = f"$\\beta$ = {popt[1]:.2f}\n$R^2$ = {r2:.2f}"
    y_loc = y_loc_up if word_up else y_loc_down
    ax.text(x_loc, y_loc, annotation_text, fontsize=15, transform=ax.transAxes)

    print(f"Power-law: y = {10**popt[0]:.2e} * x^{popt[1]:.2f}")
    return popt[1], (popt[1] - ci_b, popt[1] + ci_b), residuals

# ---------- Plotting Entrypoint ---------- #

def plot_scaling_relationships(usa_data, usa_combined_df, usa_valid_indices_no_dis, year):
    """
    Create subplots for different road types vs population scaling relationships.

    Parameters:
        usa_data               : Original USA road dataset
        usa_combined_df        : DataFrame with aggregated road length by type
        usa_valid_indices_no_dis : Boolean index for valid entries (non-zero)
        year                   : Year string (e.g. "2022")
    """
    columns = ['metro', 'motorway*', 'primary', 'secondary', 'tertiary', 'residential*', 'footway']
    pop_col = 'dp1_0001c'  # USA population column
    label_size = 18
    text_size = 16
    fig, axes = plt.subplots(nrows=4, ncols=4, figsize=(13, 12), dpi=300, sharex=True, sharey=True)
    plt.xticks([]), plt.yticks([])
    font = text_size + 3
    first = 'A'
    text_a, text_b = 0.03, 0.95  # Text position

    for idx, column in enumerate(columns, start=2):
        ax = fig.add_subplot(4, 4, idx)
        ax.set_title(f"{column.capitalize()}", fontsize=14)

        # Set axis labels for left and bottom plots
        if idx in [5, 9, 13]:
            ax.set_ylabel("Road Length (km)", fontsize=label_size)
        if idx > 12:
            ax.set_xlabel("Population", fontsize=label_size)

        # Annotate subplot
        ax.text(text_a, text_b, chr(ord(first) + idx - 1), ha="left", va="top",
                transform=ax.transAxes, fontproperties=FontProperties().set_weight("bold"),
                fontsize=font, color='black')

        # Data selection per road type
        if column == 'metro':
            x = usa_data.loc[usa_combined_df['metro'] != 0, pop_col]
            y = usa_combined_df['metro'].loc[usa_combined_df['metro'] != 0]
        else:
            x = usa_data.loc[usa_valid_indices_no_dis, pop_col]
            y = usa_combined_df[column].loc[usa_valid_indices_no_dis]

        # Plot
        logbinning_fitPower(x, y, 15, ax, f"{year} {column}", 0.7, 0.5, 0.07,
                            scatter_color="#501d8a", bin_color="#c6ccdc", bin_fit=False,
                            confidence_band=False, word_up=False)

    plt.tight_layout()
    plt.show()