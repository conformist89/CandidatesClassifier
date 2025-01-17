import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.stats import sem
from scipy.stats import binned_statistic as b_s
import matplotlib as mpl

from hipe4ml import plot_utils

def correlation_matrix(bgr, sign, vars_to_draw, leg_labels, output_path):
    res_s_b = plot_utils.plot_corr([bgr, sign], vars_to_draw, leg_labels)
    res_s_b[0].savefig(output_path+'/'+'corr_matrix_bgr.png')
    res_s_b[1].savefig(output_path+'/'+'corr_matrix_sign.png')



def calculate_correlation(df, vars_to_corr, target_var) :
    """
    Calculates correlations with target variable variable and standart errors
    Parameters
    ------------------------------------------------
    df: pandas.DataFrame
        imput data
    vars_to_corr: list of str
         variables that correlate with target value
    target_var: str
          variable that correlates with another variables mentioned in list
    """


    mean = df[target_var].mean()
    sigma = df[target_var].std()

    correlation = []
    error = []

    for j in vars_to_corr :
        mean_j = df[j].mean()
        sigma_j = df[j].std()

        cov = (df[j] - mean_j) * (df[target_var] - mean) / (sigma*sigma_j)
        correlation.append(cov.mean())
        error.append(sem(cov))

    return correlation, error


def plot1Dcorrelation(vars_to_draw,var_to_corr, corr_signal, corr_signal_errors, corr_bg, corr_bg_errors, output_path):
    """
    Plots correlations
    Parameters
    ------------------------------------------------
    vars_to_draw: list of str
        variables that correlate with target value
    var_to_corr: str
         variables that correlate with target value
    corr_signal: list
          signal covariance coefficient between variable and target variable
    corr_signal_errors:
          signal covariance standart error of the mean
    corr_bg: list
          background covariance coefficient between variable and target variable
    corr_bg_errors:
         background covariance standart error of the mean
    output_path:
          path that contains output plot
    """

    fig, ax = plt.subplots(figsize=(10,6))
    plt.errorbar(vars_to_draw, corr_signal, yerr=corr_signal_errors, fmt='--o')
    plt.errorbar(vars_to_draw, corr_bg, yerr=corr_bg_errors, fmt='--o')
    ax.grid(zorder=0)
    ax.set_xticklabels(vars_to_draw, fontsize=15, rotation =70)
    # ax.set_yticklabels([-0.5,-0.4,  -0.2,0, -0.2, 0.4], fontsize=25)
    ax.yaxis.set_tick_params(labelsize=15)
    plt.legend(('signal','background'), fontsize = 15)
    plt.title('Correlation of all variables with '+ var_to_corr+' along with SEM', fontsize = 18)
    plt.ylabel('Correlation coefficient', fontsize = 15)
    fig.tight_layout()
    fig.savefig(output_path+'/all_vars_corr-'+ var_to_corr+'.png')



def profile_mass(df,variable_xaxis, sign, peak, edge_left, edge_right, pdf_key):
    """
    This function takes the entries of the variables and distributes them in 25 bins.
    The function then plots the bin centers of the first variable on the x-axis and
    the mean values of the bins of the second variable on the y-axis, along with its bin stds.
    Parameters
    ------------------------------------------------
    df: pandas.DataFrame
        input DataFrame
    variable_xaxis: str
        variable to be plotted on x axis (invariant mass)
    x_unit: str
        x axis variable units
    variable_yaxis: str
        variable to be plotted on y axis
    sgn: int(0 or 1)
         signal definition(0 background, 1 signal)
    pdf_key: matplotlib.backends.backend_pdf.PdfPages
        output pdf file
    peak: int
        invariant mass peak position
    edge_left: int
        left edge of x axis variable
    edge_right: int
        left edge of y axis variable
    """

    if sign == 1:
        keyword = 'signal'
    if sign == 0:
        keyword = 'background'

    df = df[(df[variable_xaxis] < edge_right) & (df[variable_xaxis] > edge_left)]

    for var in df.columns:
        if var != variable_xaxis:

            fig, axs = plt.subplots(figsize=(10, 6))

            bin_means, bin_edges, binnumber = b_s(df[variable_xaxis],df[var], statistic='mean', bins=25)
            bin_std, bin_edges, binnumber = b_s(df[variable_xaxis],df[var], statistic='std', bins=25)
            bin_count, bin_edges, binnumber = b_s(df[variable_xaxis],df[var], statistic='count',bins= 25)
            bin_width = (bin_edges[1] - bin_edges[0])
            bin_centers = bin_edges[1:] - bin_width/2

            nan_ind = np.where(np.isnan(bin_means))
            bin_centers = np.delete(bin_centers, nan_ind)
            bin_means = np.delete(bin_means, nan_ind)
            bin_count = np.delete(bin_count, nan_ind)
            bin_std = np.delete(bin_std , nan_ind)


            plt.errorbar(x=bin_centers, y=bin_means, yerr=(bin_std/np.sqrt(bin_count)), linestyle='none', linewidth = 2, marker='.',mfc='red', ms=15)

            plt.locator_params(axis='y', nbins=5)
            plt.locator_params(axis='x', nbins=5)

            plt.title('Mean of ' +var+ '  vs bin centers of '+variable_xaxis+ \
                      '('+keyword+')', fontsize=19)
            plt.xlabel('Mass', fontsize=17)
            plt.ylabel(" SEM ($\dfrac{bin\ std}{\sqrt{bin\ count}}$) of bin", fontsize=17)


            plt.vlines(x=peak,ymin=bin_means.min(),ymax=bin_means.max(), color='r', linestyle='-', linewidth = 3)

            axs.xaxis.set_tick_params(labelsize=16)
            axs.yaxis.set_tick_params(labelsize=16)
            fig.tight_layout()
            plt.savefig(pdf_key,format='pdf')

    pdf_key.close()


def plot2D_all(df, sample, sgn, pdf_key):
    """
    Plots 2D distribution between all the variables
    Parameters
    ------------------------------------------------
    df: pandas.DataFrame
        input dataframe
    sample: str
         title of the sample
    sgn: int(0 or 1)
         signal definition(0 background, 1 signal)
    pdf_key: matplotlib.backends.backend_pdf.PdfPages
        output pdf file
    """

    for xvar in df.columns:
        for yvar in df.columns:
            if xvar!=yvar:
                fig, axs = plt.subplots(figsize=(15, 10))
                cax = plt.hist2d(df[xvar],df[yvar],range=[[df[xvar].min(), df[xvar].max()], [df[yvar].min(), df[yvar].max()]], bins=100,
                            norm=mpl.colors.LogNorm(), cmap=plt.cm.viridis)


                if sgn==1:
                    plt.title('Signal candidates ' + sample, fontsize = 25)

                if sgn==0:
                    plt.title('Background candidates ' + sample, fontsize = 25)


                plt.xlabel(xvar, fontsize=25)
                plt.ylabel(yvar, fontsize=25)


                mpl.pyplot.colorbar()

                plt.legend(shadow=True,title =str(len(df))+ " samples")

                fig.tight_layout()
                plt.savefig(pdf_key,format='pdf')
    pdf_key.close()


def plot2D_mass(df, sample, mass_var, mass_range, sgn, peak, pdf_key):
    """
    Plots 2D distribution between variable and invariant mass
    Parameters
    ------------------------------------------------
    df: pandas.DataFrame
        input dataframe
    sample: str
         title of the sample
    mass_var: str
        name of the invariant mass variable
    mass_range: list
        mass range to be plotted
    sgn: int(0 or 1)
         signal definition(0 background, 1 signal)
    peak: int
        invariant mass value
    pdf_key: matplotlib.backends.backend_pdf.PdfPages
        output pdf file
    """

    for var in df.columns:
        if var != mass_var:
            fig, axs = plt.subplots(figsize=(6, 4))
            cax = plt.hist2d(df[mass_var],df[var],range=[mass_range, [df[var].min(), df[var].max()]], bins=100,
                        norm=mpl.colors.LogNorm(), cmap=plt.cm.viridis)


            if sgn==1:
                plt.title('Signal candidates ' + sample, fontsize = 15)

            if sgn==0:
                plt.title('Background candidates ' + sample, fontsize = 15)


            plt.xlabel(mass_var, fontsize=16)
            plt.ylabel(var, fontsize=16)

            plt.vlines(x=peak,ymin=df[var].min(),ymax=df[var].max(), color='r', linestyle='-', linewidth = 4)

            mpl.pyplot.colorbar()


            axs.xaxis.set_tick_params(labelsize=11)
            axs.yaxis.set_tick_params(labelsize=11)

            plt.locator_params(axis='y', nbins=5)
            plt.locator_params(axis='x', nbins=5)


            plt.legend(shadow=True,title =str(len(df))+ " samples")

            fig.tight_layout()
            plt.savefig(pdf_key,format='pdf')
    pdf_key.close()
