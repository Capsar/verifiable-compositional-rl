from typing import Dict
import numpy as np
import cvxpy as cp

def solve_optimistic_irl(mdp, feature_counts):
    """
    Solve an inverse reinforcement learning problem.
    """
    pass

def solve_optimistic_forward_problem(problem : dict,
                                    reward_vec : np.ndarray):
    """
    Solve the forward pass of the inverse reinforcement learning problem.
    This corresponds to solving a maximum entropy dynamic programming problem 
    with a given reward vector.

    Parameters
    ----------
    problem : 
        A dictionary containing a cvxpy optimization problem (problem['problem']),
        its variables (problem['vars']), and its parameters (problem['params']).
    reward_vec : 
        A (N_S, N_A) numpy array representing the reward vector to use in 
        solving the forward optimization problem.
    """
    assert (problem['params']['reward_vec'].value.shape == reward_vec.shape)
    problem['params']['reward_vec'].value = reward_vec
    return problem['problem'].solve

def state_feature_count_difference(demo_feature_count, opt_state_vars):
    diff = np.zeros(demo_feature_count.shape)
    for s in range(len(demo_feature_count)):
        diff[s] = opt_state_vars[s] - demo_feature_count[s]
    return diff

def construct_optimistic_irl_forward_pass(mdp):
    #dictionary for state occupancy and state action occupancy
    state_vars = dict()
    state_act_vars = dict()

    avail_actions = mdp.avail_actions.copy()

    #dummy action for goal state
    # avail_actions[mdp.s_g] = [0]

    #create occupancy measures, probability variables and reward variables
    for s in mdp.S:
        state_vars[s] = cp.Variable(name="state_"+str(s), nonneg=True)

        for a in avail_actions[s]:
            state_act_vars[(s, a)] = cp.Variable(name="state_act_"+str(s)+"_"+str(a), 
                                                nonneg=True)

    vars = {
        'state_act_vars' : state_act_vars,
        'state_vars' : state_vars
    }
    
    # Create problem parameters
    reward_vec = cp.Parameter(shape=(mdp.N_S, mdp.N_A), 
                                name='reward_vec',
                                value=np.zeros((mdp.N_S, mdp.N_A)))
    params = {
        'reward_vec' : reward_vec
    }

    ###### define the problem constraints
    cons = []

    #MDP bellman or occupancy constraints for each state
    for s in mdp.S:
        cons_sum=0
        # #add outgoing occupancy for available actions
        # for a in avail_actions[s]:
        #     cons_sum += state_act_vars[s,a]

        cons_sum += state_vars[s]

        #add ingoing occupancy for predecessor state actions
        for s_bar, a_bar in mdp.predecessors[s]:
            # #this if clause ensures that you dont double count reaching goal and failure
            # if not s_bar == mdp.s_g and not s_bar == mdp.s_fail:
            cons_sum -= mdp.discount * state_act_vars[s_bar, a_bar] * 1.0 #mdp.P[s_bar, a_bar, s]
        #initial state occupancy
        if s == mdp.s_i:
            cons_sum = cons_sum - 1

        #sets occupancy constraints
        cons.append(cons_sum == 0)

    # Define relation between state-action occupancy measures 
    # and state occupancy measures
    for s in mdp.S:
        cons_sum = cp.sum([state_act_vars[s,a] for a in avail_actions[s]])
        cons.append(state_vars[s] == cons_sum)

    # set up the objective
    obj_sum = 0

    for s in mdp.S:
        for a in avail_actions[s]:
            # obj_sum -= (cp.log(state_act_vars[s, a]) - cp.log(state_vars[s])) * state_act_vars[s,a]
            obj_sum -= cp.rel_entr(state_act_vars[s,a], state_vars[s])
            obj_sum += reward_vec[s, a] * state_act_vars[s,a]

    obj = cp.Maximize(obj_sum)

    prob = cp.Problem(objective=obj, constraints=cons)

    forward_problem = {
        'problem' : prob,
        'vars' : vars,
        'params' : params
    }

    return forward_problem

    # if linear_model.SolCount == 0:
    #     feasible_flag = False
    # else:
    #     feasible_flag = True

    # if feasible_flag:
    #     # Construct the policy from the occupancy variables
    #     policy = np.zeros((self.N_S, self.N_A), dtype=np.float)
    #     for s in self.S:
    #         if len(self.avail_actions[s]) == 0:
    #             policy[s, :] = -1 # If no actions are available, return garbage value
    #         else:
    #             occupancy_state = np.sum([state_act_vars[s,a].x for a in self.avail_actions[s]])
    #             # If the state has no occupancy measure under the solution, set the policy to 
    #             # be uniform over available actions
    #             if occupancy_state == 0.0:
    #                 for a in self.avail_actions[s]:
    #                     policy[s,a] = 1 / len(self.avail_actions[s])
    #             if occupancy_state > 0.0:
    #                 for a in self.avail_actions[s]:
    #                     policy[s, a] = state_act_vars[s,a].x / occupancy_state
    # else:
    #     policy = -1 * np.ones((self.N_S, self.N_A), dtype=np.float)

    # return policy, feasible_flag