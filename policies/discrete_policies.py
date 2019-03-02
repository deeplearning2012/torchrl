import torch
import torch.nn as nn

import numpy as np
import networks

class UniformPolicyDiscrete(nn.Module):
    def __init__(self, action_num):
        super().__init__()
        self.action_num = action_num

    def forward(self,x ):
        return np.random.randint(self.action_num)

    def explore(self, x):
        return {"action":np.random.randint(self.action_num)}

class EpsilonGreedyDQNDiscretePolicy():
    """
    wrapper over QNet
    """
    def __init__(self, qf, start_epsilon, end_epsilon, decay_frames, action_shape):
        self.qf = qf
        self.start_epsilon = start_epsilon
        self.end_epsilon = end_epsilon
        self.decay_frames = decay_frames
        self.count = 0
        self.action_shape = action_shape
        self.epsilon = self.start_epsilon
    
    def q_to_a(self, q):
        return q.max(dim=-1)[1].detach().item()

    def explore(self, x):
        self.count += 1
        r = np.random.rand()
        if self.count < self.decay_frames:
            self.epsilon =  self.start_epsilon - ( self.start_epsilon - self.end_epsilon ) \
                * ( self.count / self.decay_frames )
        else:
            self.epsilon = self.end_epsilon
        
        if r < self.epsilon:
            return {
                "action":np.random.randint(0, self.action_shape )
            }
    
        output = self.qf(x)
        action = self.q_to_a(output)
        return {
            "q_value": output,
            "action":action
        }
    
    def eval(self, x):
        output = self.qf(x)
        action = self.q_to_a(output)
        return action

class EpsilonGreedyQRDQNDiscretePolicy(EpsilonGreedyDQNDiscretePolicy):
    """
    wrapper over QNet
    """
    def __init__(self, quantile_num, **kwargs):
        super(EpsilonGreedyQRDQNDiscretePolicy,self).__init__( **kwargs)
        self.quantile_num = quantile_num

    def q_to_a(self, q):
        q = q.view(-1, self.action_shape, self.quantile_num)
        return q.mean(dim=-1).max(dim=-1)[1].detach().item()

class BootstrappedDQNDiscretePolicy():
    """
    wrapper over QNet
    """
    def __init__(self, qf, head_num, action_shape):
        self.qf = qf
        self.head_num = head_num
        self.action_shape = action_shape
        self.idx = 0

    def sample_head(self):
        self.idx = np.random.randint(self.head_num)

    def explore(self, x):
        output = self.qf( x, [ self.idx ] )
        action = output[0].max(dim=-1)[1].detach().item()
        return {
            "q_value": output[0],
            "action":action
        }
    
    def eval(self, x):
        output = self.qf( x, range(self.head_num) )
        output = torch.mean( torch.cat(output, dim=0 ), dim=0 )
        action = output.max(dim=-1)[1].detach().item()
        return action
