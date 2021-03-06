from collections import namedtuple

experiment_name_ext = '_8x4'

# TwoGoalGridWorld environment variables
EnvParam = namedtuple('EnvironmentParameters',
                     ['shape',
                      'r_correct',
                      'r_incorrect',
                      'r_step',
                      'r_wall',
                      'p_rand',
                      'goal_locs',
                      'goal_dist'])
env_param = EnvParam(shape = [8,4],
                     r_correct = +1,
                     r_incorrect = -1,
                     r_step = 0.,
                     r_wall = -.1,
                     p_rand = 0,
                     goal_locs = [1,2],
                     goal_dist = None)

def get_config():
    return env_param, experiment_name_ext