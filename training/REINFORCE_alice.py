import numpy as np
import itertools
import copy
from collections import namedtuple

EpisodeStats = namedtuple('Stats', ['episode_lengths', 'episode_rewards', 'episode_kls'])
Transition = namedtuple('Transition', ['state', 'action', 'reward'])

def reinforce(env, policy_estimator, value_estimator, num_episodes,
              entropy_scale, beta, discount_factor, max_episode_length):
    """
    REINFORCE (Monte Carlo Policy Gradient) Algorithm. Optimizes the policy
    function approximator using policy gradient.
    
    Args:
        env: OpenAI environment.
        policy: policy to be optimized 
        value: value function approximator, used as a baseline
        num_episodes: mumber of episodes to run for
        entropy_scale: vector of length num_episodes
        discount_factor: time-discount factor
    
    Returns:
        An EpisodeStats object with two numpy arrays for episode_lengths and episode_rewards.
    """
    
    # this allows one to set params to scalars when not wanting to anneal them
    if not isinstance(entropy_scale, (list, np.ndarray)):
        entropy_scale = [entropy_scale]*num_episodes
    if not isinstance(beta, (list, np.ndarray)):
        beta = [beta]*num_episodes

    # Keeps track of useful statistics
    stats = EpisodeStats(
        episode_lengths = np.zeros(num_episodes),
        episode_rewards = np.zeros(num_episodes),
        episode_kls = np.zeros(num_episodes))    
    
    for i_episode in range(num_episodes):
        # Reset the environment and pick the first action
        state, goal = env.reset()
        
        episode = []
        
        # One step in the environment
        for t in itertools.count(start = 1):
            
            # Take a step
            action_probs = policy_estimator.predict(state, goal)
            kl = policy_estimator.get_kl(state, goal)
            action = np.random.choice(np.arange(len(action_probs)), p = action_probs)
            next_state, reward, done, _ = env.step(action)
            
            # Keep track of the transition
            episode.append(Transition(state = state, action = action, reward = reward))
            
            # Update statistics
            stats.episode_rewards[i_episode] += reward
            stats.episode_lengths[i_episode] = t
            stats.episode_kls[i_episode] += kl
            
            # Print out which step we're on, useful for debugging.
            print("\rStep {} @ Episode {}/{} ({})".format(
                    t, i_episode + 1, num_episodes, stats.episode_rewards[i_episode - 1]), end="")
            # sys.stdout.flush()

            if done or t > max_episode_length: break
                
            state = next_state
    
        # Go through the episode and make policy updates
        for t, transition in enumerate(episode):
            # The return after this timestep
            total_return = sum(discount_factor**i * t.reward for i, t in enumerate(episode[t:]))
            # Update our value estimator
            value_estimator.update(transition.state, goal, total_return)
            # Calculate baseline/advantage
            baseline_value = value_estimator.predict(transition.state, goal)            
            advantage = total_return - baseline_value
            # Update our policy estimator
            policy_estimator.update(transition.state,
                                    goal,
                                    advantage,
                                    transition.action,
                                    entropy_scale[i_episode],
                                    beta[i_episode])
    
    return stats