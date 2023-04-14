# %%

import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import tikzplotlib

sys.path.append('..')
from utils.results_saver import Results


def get_results(load_folder_name):
    base_path = os.path.abspath(os.path.curdir)
    string_ind = base_path.find('src')
    assert (string_ind >= 0)
    base_path = base_path[0:string_ind + 4]
    base_path = os.path.join(base_path, 'data', 'saved_controllers')
    load_dir = os.path.join(base_path, load_folder_name)
    results = Results(load_dir=load_dir)
    return results


def plot_results(results, experiment_name, ax):
    timesteps = results.data['cparl_loop_training_steps']
    controller_training_steps = results.data['controller_elapsed_training_steps']
    large_linewidth = 10
    large_marker_size = 650
    ax.set_title(experiment_name)
    ax.set_ylabel('Controller')
    ax.grid()
    ax.set_yticks([i for i in controller_training_steps.keys()])
    ax.set_xticks(timesteps)
    ax.set_xlim([timesteps[0], timesteps[-1]])

    ttwenty = matplotlib.colormaps['tab20']
    for t in range(len(timesteps) - 1):
        curr_time = timesteps[t]
        next_time = timesteps[t + 1]
        for controller_ind in controller_training_steps.keys():
            if not controller_training_steps[controller_ind][curr_time] == controller_training_steps[controller_ind][next_time]:
                ax.plot([curr_time, next_time], [controller_ind, controller_ind], linewidth=large_linewidth, color=ttwenty(controller_ind))

    yl = ax.get_ylim()
    ax.set_ylim(yl)
    # ax.plot([6.5e5, 6.5e5], [yl[0], yl[1]], color='red', linewidth=large_linewidth * 0.7, linestyle='--')


if __name__ == '__main__':

    new_load_folder_name = '2023-04-13_17-59-47_minigrid_labyrinth'
    new_experiment_name = 'new_minigrid_labyrinth_new_optimization'

    old_load_folder_name = '2023-04-13_18-35-30_minigrid_labyrinth'
    old_experiment_name = 'new_minigrid_labyrinth_old_optimization'

    new_results = get_results(new_load_folder_name)
    old_results = get_results(old_load_folder_name)

    fig, axes = plt.subplots(2, 1, figsize=(12, 5), sharex=True)

    plt.rcParams["figure.autolayout"] = True
    plot_results(new_results, new_experiment_name, axes[0])
    plot_results(old_results, old_experiment_name, axes[1])
    axes[1].set_xlabel('Timesteps')
    plt.xticks(rotation=-45)
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    plt.gca().ticklabel_format(useMathText=True)
    plt.tight_layout()

    plt.savefig(os.path.join(os.path.curdir, 'figures/comparison_training_schedule_new_example.svg'))
    plt.show()
