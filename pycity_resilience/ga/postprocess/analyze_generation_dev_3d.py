#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import os
import pickle
import warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib as mpl
import itertools
# from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits import mplot3d

try:
    from matplotlib2tikz import save as tikz_save
except:
    msg = 'Could not import matplotlib2tikz'
    warnings.warn(msg)

try:
    import terminaltables
except:
    msg = 'Could not import termnaltables packages. Thus, cannot use ' \
          'function print_ind_esys_sol_details()!'
    warnings.warn(msg)

#  Attention: You have to set an 3d objective in opt_ga.py before doing the
#  import!!! Otherwise the 3rd objective function values will not be loaded.
import pycity_resilience.ga.opt_ga  # Necessary to load pickle files!
from deap import base, creator, tools, algorithms


def main():
    #  Define pathes
    #  ####################################################################
    this_path = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.dirname(os.path.dirname(os.path.dirname(this_path)))
    workspace = os.path.join(src_path, 'workspace')

    name_res_folder = 'ga_run_3d_2nd'
    path_results = os.path.join(workspace,
                                'output',
                                'ga_opt',
                                # 'analysis_new_b_3D',
                                name_res_folder)

    out_name = name_res_folder + '_dict_par_front_sol.pkl'
    path_save_par = os.path.join(workspace,
                                 'output',
                                 'ga_opt',
                                 out_name)

    nb_ind_used = 400

    list_inds_pareto = analyze_pareto_sol_3d(path_results_folder=path_results,
                                             nb_ind_used=nb_ind_used)

    #  Parse list of pareto solutions to dict (nb. as keys to re-identify
    #  each solution
    dict_pareto_sol = {}
    for i in range(len(list_inds_pareto)):
        dict_pareto_sol[int(i + 1)] = list_inds_pareto[i]

    #  Save pareto dict to path
    pickle.dump(dict_pareto_sol, open(path_save_par, mode='wb'))


def load_res(dir, fileending='.pkl'):
    """
    Load ga results from path

    Parameters
    ----------
    dir : str
        Path to results folder
    fileending : str, optional
        Fileending (default: '.pkl')

    Returns
    -------
    dict_gen : dict
        Dict holding generation number as key and population object as value
    """

    list_pkl_files = []
    for file in os.listdir(dir):
        if file.endswith(fileending) and file.startswith('population'):
            list_pkl_files.append(file)

    # for entry in list_pkl_files:
    #     print(entry)

    # file_in = os.path.join(path_results_folder, list_pkl_files[0])
    # pop = pickle.load(open(file_in, mode='rb'))

    # #     ind.fitness.values
    # for ind in pop:
    #     print('Population: ', pop)
    #     print('Fitness: ', ind.fitness.values)

    dict_gen = {}
    #  Sort list in order
    for entry in list_pkl_files:
        print(entry)

        #  Load each entry
        path_pkl_in = os.path.join(dir, entry)
        pop = pickle.load(open(path_pkl_in, mode='rb'))

        if len(entry) == 16:  # e.g. population_0.pkl
            #  Extract nb. with one entry
            nb_pop = int(entry[11])
        elif len(entry) == 17:  # e.g. population_10.pkl
            nb_pop = int(entry[11:13])
        elif len(entry) == 18:  # e.g. population_100.pkl
            nb_pop = int(entry[11:14])
        elif len(entry) == 19:  # e.g. population_100.pkl
            nb_pop = int(entry[11:15])
        else:
            raise AssertionError()

        # Save to dict
        dict_gen[nb_pop] = pop

    return dict_gen


def print_gen_sol_dev(dict_gen, path_save=None, output_filename='ga_gen_dev',
                      dpi=100):
    """

    Parameters
    ----------
    dict_gen : dict
        Dict holding generation number as key and population object as value
    path_save : str, optional
        Folder path to save plots to (default: None).
        If None, does not save figures
    output_filename : str, optional
        Output filename (default: 'ga_gen_dev'). Only relevant, if path_save
        is not None.
    dpi : int, optional
        dpi size (default: 300)

    Returns
    -------

    """

    fig = plt.figure()

    # ax = fig.add_subplot(111, projection='3d')
    ax = plt.axes(projection='3d')

    #  Generate colormap with 'jet' style
    values = range(len(list(dict_gen.keys())))
    jet = cm = plt.get_cmap('jet')
    cNorm = colors.Normalize(vmin=0, vmax=values[-1])
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

    for key in sorted(list(dict_gen.keys())):

        print('Key: ', key)

        #  Get population
        pop = dict_gen[key]

        #  Gen color
        # color = np.random.rand(3, )
        #  Get color of colormap
        color = scalarMap.to_rgba(values[int(key - 1)])

        # #  Gen markers
        # #  Caution: Causing error in tikz (for whatever reason...)
        # if key <= 50:
        #     marker = 'v'
        # elif key <= 100:
        #     marker = 's'
        # elif key <= 150:
        #     marker = '^'
        # elif key <= 200:
        #     marker = 'x'
        # elif key <= 300:
        #     marker = 'o'
        marker = 'o'

        list_ann = []
        list_co2 = []
        list_flex = []

        #  Loop over individuals
        for ind in pop:
            #  Get annuity
            ann = ind.fitness.values[0]
            co2 = ind.fitness.values[1]
            flex = ind.fitness.values[2]

            if isinstance(ann, float) and isinstance(co2, float) \
                    and isinstance(flex, float):
                if ann < 10 ** 90:  # Smaller than penalty function
                    list_ann.append(ann)
                if co2 < 10 ** 90:  # Smaller than penalty function
                    list_co2.append(co2)
                if flex > -10 ** 90:
                    list_flex.append(flex)

        # #  Convert from Euro to kilo-Euro and kilograms to tons CO2
        # for i in range(len(list_ann)):
        #     list_ann[i] /= 1000
        #     list_co2[i] /= 1000

        # if len(dict_gen.keys()) - key <= 10:
        if key in [1, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500]:
            ax.plot3D(xs=list_ann,
                      ys=list_co2,
                      zs=list_flex,
                      marker=marker,
                      linestyle='',
                      markersize=3,
                      c=color,
                      label=str('Generation' + str(key)))
        else:
            ax.plot3D(xs=list_ann,
                      ys=list_co2,
                      zs=list_flex,
                      marker=marker,
                      linestyle='',
                      markersize=3,
                      c=color)

    ax.set_xlabel('Dimensionless cost')
    ax.set_ylabel('Dimensionless emissions')
    ax.set_zlabel('Dimensionless flexibility')
    plt.legend()
    plt.tight_layout()

    if path_save is not None:

        if not os.path.exists(path_save):
            os.makedirs(path_save)

        #  Generate file names for different formats
        file_pdf = output_filename + '.pdf'
        file_eps = output_filename + '.eps'
        file_png = output_filename + '.png'
        file_tikz = output_filename + '.tikz'
        file_svg = output_filename + '.svg'

        #  Generate saving pathes
        path_pdf = os.path.join(path_save, file_pdf)
        path_eps = os.path.join(path_save, file_eps)
        path_png = os.path.join(path_save, file_png)
        path_tikz = os.path.join(path_save, file_tikz)
        path_svg = os.path.join(path_save, file_svg)

        #  Save figure in different formats
        plt.savefig(path_pdf, format='pdf', dpi=dpi)
        plt.savefig(path_eps, format='eps', dpi=dpi)
        plt.savefig(path_png, format='png', dpi=dpi)
        plt.savefig(path_svg, format='svg', dpi=dpi)

        try:
            tikz_save(path_tikz, figureheight='\\figureheight',
                      figurewidth='\\figurewidth')
        except:
            msg = 'tikz_save command failed. Could not save figure to tikz.'
            warnings.warn(msg)

    plt.show()
    plt.close()


def print_ind_esys_sol_overview(ind):
    """
    Print overview of energy system solution on individuum, including
    Number of devices and LHN connected building nodes

    Parameters
    ----------
    ind : object
        Individuum object of pyCity_resilience
    """

    #  List holding strings with solution info
    dict_nb_esys = {'boi': 0,
                    'chp': 0,
                    'hp_aw': 0,
                    'hp_ww': 0,
                    'eh': 0,
                    'tes': 0,
                    'pv': 0,
                    'bat': 0}
    list_lhn = []

    #  Loop over buildings
    for key in ind.keys():
        if key != 'lhn':
            for esyskey in dict_nb_esys.keys():
                if ind[key][esyskey] > 0:
                    dict_nb_esys[esyskey] += 1

        elif key == 'lhn':
            if len(ind['lhn']) > 0:
                for list_sub_lhn in ind['lhn']:
                    list_lhn.append(list_sub_lhn)

    print('#################################################')
    print('Fitness values:')
    print('Annuity: ', ind.fitness.values[0])
    print('CO2: ', ind.fitness.values[1])
    print()

    print('Solution config:')
    print('Boilers: ', dict_nb_esys['boi'])
    print('CHPs: ', dict_nb_esys['chp'])
    print('LHNs: ', len(list_lhn))
    if len(list_lhn) > 0:
        print('LHN nodes: ', list_lhn)
    print('HP (aw): ', dict_nb_esys['hp_aw'])
    print('HP (ww): ', dict_nb_esys['hp_ww'])
    print('PV: ', dict_nb_esys['pv'])
    print('#################################################')
    print()


def print_res_final_pop(list_ann, list_co2, list_flex):
    """
    Print results of final population

    Parameters
    ----------
    list_ann
    list_co2
    list_flex
    """

    fig = plt.figure()

    # ax = fig.add_subplot(111, projection='3d')
    ax = plt.axes(projection='3d')

    ax.plot3D(xs=list_ann,
              ys=list_co2,
              zs=list_flex,
              marker='o',
              linestyle='',
              markersize=5,
              c='#E53027')

    ax.set_xlabel('Dimensionless cost')
    ax.set_ylabel('Dimensionless emissions')
    ax.set_zlabel('Dimensionless flexibility')
    plt.tight_layout()
    plt.show()
    plt.close()


def print_ind_esys_sol_details(ind):
    """
    Prints details of energy system config per building

    Parameters
    ----------
    ind : object
        Individuum object of pyCity_resilience
    """

    list_esys = ['boi',
                 'chp',
                 'hp_aw',
                 'hp_ww',
                 'eh',
                 'tes',
                 'pv',
                 'bat']

    list_header = ['Type', 'Unit']
    list_boi = ['Boiler', 'kW']
    list_chp = ['CHP', 'kW (th.)']
    list_hp_aw = ['HP (aw)', 'kW (th.)']
    list_hp_ww = ['HP (ww)', 'kW (th.)']
    list_eh = ['EH', 'kW']
    list_tes = ['Storage', 'liters']
    list_pv = ['PV', 'm2']
    list_bat = ['Bat', 'kWh']
    list_lhn = ['LHN(s) indexes', '-']

    #  Loop over buildings
    for key in ind.keys():
        if key != 'lhn':  # Building id
            list_header.append(key)
            for esys in list_esys:
                if esys == 'boi':
                    list_boi.append(ind[key][esys] / 1000)
                elif esys == 'chp':
                    list_chp.append(ind[key][esys] / 1000)
                elif esys == 'hp_aw':
                    list_hp_aw.append(ind[key][esys] / 1000)
                elif esys == 'hp_ww':
                    list_hp_ww.append(ind[key][esys] / 1000)
                elif esys == 'eh':
                    list_eh.append(ind[key][esys] / 1000)
                elif esys == 'tes':
                    list_tes.append(ind[key][esys])
                elif esys == 'pv':
                    list_pv.append(ind[key][esys])
                elif esys == 'bat':
                    list_bat.append(ind[key][esys] / (1000 * 3600))

            found_con = False
            #  Search, if building is connected to lhn
            if len(ind['lhn']) > 0:
                for i in range(len(ind['lhn'])):  # Loop over sub-networks
                    if key in ind['lhn'][i]:  # Search for existence of node
                        list_lhn.append(str(i))
                        found_con = True
                        break
            if found_con is False:
                list_lhn.append('x')

    table_data = []
    table_data.append(list_header)
    if sum(list_boi[2:]) > 0:
        table_data.append(list_boi)
    if sum(list_chp[2:]) > 0:
        table_data.append(list_chp)
    if sum(list_hp_aw[2:]) > 0:
        table_data.append(list_hp_aw)
    if sum(list_hp_ww[2:]) > 0:
        table_data.append(list_hp_ww)
    if sum(list_eh[2:]) > 0:
        table_data.append(list_eh)
    if sum(list_tes[2:]) > 0:
        table_data.append(list_tes)
    if sum(list_pv[2:]) > 0:
        table_data.append(list_pv)
    if sum(list_bat[2:]) > 0:
        table_data.append(list_bat)
    table_data.append(list_lhn)

    table = terminaltables.AsciiTable(table_data=table_data)

    print(table.table)


def get_final_pop(dict_gen):
    """
    Returns final population of results dict

    Parameters
    ----------
    dict_gen : dict
        Dict holding generation number as key and population object as value

    Returns
    -------
    tup_res : tuple
        Results tuple (final_pop, list_ann, list_co2, list_flex)
    """

    #  Get final population
    #  ###################################################################
    final_pop = dict_gen[max(dict_gen.keys())]

    list_ann = []
    list_co2 = []
    list_flex = []

    print()
    print('Final population results:')
    print('##############################################################')

    #  Loop over individuals
    for ind in final_pop:
        #  Get annuity
        ann = ind.fitness.values[0]
        co2 = ind.fitness.values[1]
        flex = ind.fitness.values[2]

        print(ind)
        print('Fitnesses: ' + str(ann) + ', ' + str(co2) + ', ' + str(flex))

        if isinstance(ann, float) and isinstance(co2, float):
            list_ann.append(ann)
            list_co2.append(co2)
            list_flex.append(flex)

    return (final_pop, list_ann, list_co2, list_flex)


def get_par_front_list_of_final_pop(final_pop):
    """
    Returns list with individuals of final pareto frontier

    Parameters
    ----------
    final_pop : object
        Final population object

    Returns
    -------
    list_inds_pareto : list
        List holding pareto optimal ind solutions (sorted by fitness values,
        beginning with lowest cost value)
    """

    print()
    print('Non-dominated pareto-frontier results:')
    print('##############################################################')

    #  Get pareto frontier results (first/best pareto frontier)
    lists_pareto_frontier = tools.sortNondominated(final_pop, len(final_pop),
                                                   first_front_only=True)

    list_inds_pareto = []

    #  Add all solutions of lists_pareto_frontier to single list
    for list_par in lists_pareto_frontier:
        for sol in list_par:
            list_inds_pareto.append(sol)

    #  Sort by fitness value
    list_inds_pareto = sorted(list_inds_pareto,
                              key=lambda x: x.fitness.values[0],
                              reverse=False)

    return list_inds_pareto


def get_esys_pareto_info(list_pareto_sol, ncol=2, use_dist_point=True):
    """
    Get information about esys development along pareto frontier

    Parameters
    ----------
    list_pareto_sol : list
        List holding individuums of pareto frontier
    ncol : int, optional
        Number of columns in legend
    use_dist_point : bool, optional
        Defines, if invisible distance point should be used, based on
        max. cost value plus 20 % buffer (default: True)
    """

    list_pareto_sorted = sorted(list_pareto_sol,
                                key=lambda x: x.fitness.values[0],
                                reverse=False)

    max_flex = 0

    for sol in list_pareto_sorted:
        print(sol)
        print('Fitnesses: ', sol.fitness.values)
        if sol.fitness.values[2] > max_flex:
            max_flex = sol.fitness.values[2] + 0.0

    # if max_flex > 1000:
    #     max_flex = round(max_flex/1000) * 1000
    # elif max_flex > 100:
    #     max_flex = round(max_flex/100) * 100
    # elif max_flex > 10:
    #     max_flex = round(max_flex/10) * 10
    #
    # print(max_flex)

    print()
    print('Development along pareto frontier (from small to large cost values')
    print('#################################################################')
    for i in range(len(list_pareto_sorted)):
        print('Solution nb: ', i + 1)
        ind = list_pareto_sorted[i]
        print_ind_esys_sol_overview(ind=ind)
        print()

    for i in range(len(list_pareto_sorted)):
        print('Detailed solution nb: ', i + 1)
        ind = list_pareto_sorted[i]
        print_ind_esys_sol_details(ind)
        print()

    min_flex = 0
    step = 10
    # max_flex = 1400

    # #  Use jet colormap
    # values = range(int(max_flex - min_flex))
    # mymap = plt.get_cmap('jet')
    # cNorm = colors.Normalize(vmin=min(values), vmax=max(values))
    # scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=mymap)

    #  Use mycolor blue red colormap
    mymap = mpl.colors.LinearSegmentedColormap.from_list('mycolors',
                                                         ['blue', 'red'])

    # Using contourf to provide my colorbar info, then clearing the figure
    Z = [[0, 0], [0, 0]]
    levels = range(min_flex, int(max_flex + step), step)
    CS3 = plt.contourf(Z, levels, cmap=mymap)
    plt.clf()
    #  Source: https://stackoverflow.com/questions/8342549/matplotlib-add-colorbar-to-a-sequence-of-line-plots

    for i in range(len(list_pareto_sorted)):
        sol = list_pareto_sorted[i]

        # if int(i + 1) % 10 == 0:
        #     label = str(i + 1)
        # else:
        #     label = ''

        # #  For jet colormap
        # color = scalarMap.to_rgba(float(sol.fitness.values[2]))

        #  For mycolor blue red colormap
        #  setting rgb color based on z normalized to my range
        r = (float(sol.fitness.values[2]) - min_flex) / (max_flex - min_flex)
        g = 0
        b = 1 - r

        plt.plot([sol.fitness.values[0]],
                 [sol.fitness.values[1]],
                 marker='o',
                 # color=color
                 color=(r, g, b)
                 # ,label=label
                 )

        # if int(i + 1) % 50 == 0:
        #     #  Plot annutation
        #     ax = plt.gca()
        #     ax.annotate(str(i + 1), xy=(sol.fitness.values[0] + 100,
        #                                 sol.fitness.values[1] + 100))

    # if use_dist_point:
    #     sol = list_pareto_sorted[int(len(list_pareto_sorted)) - 1]
    #     plt.plot([sol.fitness.values[0] * 1.2],
    #              sol.fitness.values[1],
    #              color='white')

    cbar = plt.colorbar(CS3)  # using the colorbar info I got from contourf
    cbar.set_label('Dimensionless flexibililty', rotation=270, labelpad=15)

    plt.xlabel('Dimensionless cost')
    plt.ylabel('Dimensionless emissions')
    # plt.title('Non-dominated pareto results')
    # plt.legend(ncol=ncol)
    plt.tight_layout()
    plt.show()
    plt.close()


def get_pareto_front(dict_gen, size_used=None, nb_ind_used=None):
    """
    Returns list of inds, which are pareto optimal. Uses NSGA2 sorting
    algorithm with all populations, that existed.
    Runtime intensive!

    Parameters
    ----------
    dict_gen : dict
        Dict holding generation number as key and population object as value
    size_used : int, optional
        Defines size of last number of generations, which should be used
        in NSGA-2 sorting (default: None). If None, uses all generations.
    nb_ind_used : int, optional
        Number of pareto-optimal solutions, which should be extracted
        (default: None). If None, nb_ind_used is equal to size of population
        respectively number of individuals per population

    Returns
    -------
    list_inds_pareto : list (of inds)
        List holding pareto optimal individuals
    """

    last_key = max(dict_gen.keys())

    list_relevant_keys = [last_key]

    if size_used is None:
        length_val = len(dict_gen) - 1
    else:
        length_val = size_used + 0.0

    new_key = last_key + 0.0
    for i in range(length_val):
        new_key -= 1
        list_relevant_keys.append(new_key)

    list_relevant_inds = []

    for key in list_relevant_keys:
        curr_pop = dict_gen[key]
        # #  Get pareto frontier results (first/best pareto frontier)
        # list_cur_par = tools.sortNondominated(curr_pop, len(curr_pop),
        #                                       first_front_only=True)[0]
        #  Append list_relevant_inds
        for curr_ind in curr_pop:
            list_relevant_inds.append(curr_ind)

    # lists_pareto_frontier = tools.sortNondominated(list_relevant_inds,
    #                                                k=len_single_ind,
    #                                                first_front_only=True)

    # list_inds_pareto = []
    #
    # #  Add all solutions of lists_pareto_frontier to single list
    # for list_par in lists_pareto_frontier:
    #     for sol in list_par:
    #         list_inds_pareto.append(sol)
    #
    # #  Sort by fitness value
    # list_inds_pareto = sorted(list_inds_pareto,
    #                           key=lambda x: x.fitness.values[0],
    #                           reverse=False)

    if nb_ind_used is None:
        len_single_ind = len(dict_gen[0])
    else:
        len_single_ind = int(nb_ind_used + 0)

    lists_pareto_frontier = tools.selNSGA2(list_relevant_inds,
                                           k=len_single_ind)

    # lists_pareto_frontier = tools.selBest(list_relevant_inds,
    #                                       k=len_single_ind)

    #  Sort by fitness value
    lists_pareto_frontier = sorted(lists_pareto_frontier,
                                   key=lambda x: x.fitness.values[0],
                                   reverse=False)

    return lists_pareto_frontier


def analyze_pareto_sol_3d(path_results_folder, size_used=None,
                          nb_ind_used=None):
    """
    Perform overall analysis (for 3d objectives)

    Parameters
    ----------
    path_results_folder : str
        Path to results folder, holding pickled population files
    size_used : int, optional
        Defines size of last number of generations, which should be used
        in NSGA-2 sorting (default: None). If None, uses all generations.
    nb_ind_used : int, optional
        Number of pareto-optimal solutions, which should be extracted
        (default: None). If None, nb_ind_used is equal to size of population
        respectively number of individuals per population

    Returns
    -------
    list_inds_pareto : list (of inds)
        List holding individuals on pareto-frontier
    """

    #  Load results
    dict_gen = load_res(dir=path_results_folder)

    #  Plot development of generations
    print_gen_sol_dev(dict_gen=dict_gen)

    #  Extract final population
    (final_pop, list_ann, list_co2, list_flex) = get_final_pop(
        dict_gen=dict_gen)

    #  Print results of final population
    print_res_final_pop(list_ann=list_ann, list_co2=list_co2,
                        list_flex=list_flex)

    #  Extract list of pareto optimal results in final population
    list_inds_final = get_par_front_list_of_final_pop(final_pop)

    #  Extract list of pareto-optimal results from overall populations
    list_inds_pareto = get_pareto_front(dict_gen=dict_gen,
                                        size_used=size_used,  # Nb. Gen.
                                        nb_ind_used=nb_ind_used)  # Nb. ind.

    #  Print pareto front and energy system configurations
    get_esys_pareto_info(list_pareto_sol=list_inds_pareto)

    return list_inds_pareto


if __name__ == '__main__':
    main()
