import torch
from torch import nn
import torch.nn.functional as F
from src.tools.utils import make_layers


class Encoder(nn.Module):
    def __init__(self, subnets, rnns, seq_len):
        super().__init__()
        assert len(subnets)==len(rnns)

        self.blocks = len(subnets)
        self.seq_len = seq_len

        for index, (subnet, rnn) in enumerate(zip(subnets, rnns), 1):
            setattr(self, 'stage'+str(index), subnet)
            setattr(self, 'rnn'+str(index), rnn)

    def forward_by_stage(self, input_, subnet, rnn):
        batch_size, seq_number, input_channel, height, width = input_.shape
        input_ = torch.reshape(input_, (-1, input_channel, height, width))
        input_ = subnet(input_)
        input_ = torch.reshape(input_, (batch_size, seq_number, input_.shape[1], input_.shape[2], input_.shape[3]))
        outputs_stage, state_stage = rnn(input_, None, self.seq_len)

        return outputs_stage, state_stage

    # input_: 5D S*B*I*H*W
    def forward(self, input_):
        hidden_states = []
        for i in range(1, self.blocks+1):
            input_, state_stage = self.forward_by_stage(input_, getattr(self, 'stage'+str(i)), getattr(self, 'rnn'+str(i)))
            hidden_states.append(state_stage)
        return tuple(hidden_states)


class Forecaster(nn.Module):
    def __init__(self, subnets, rnns, seq_len):
        super().__init__()
        assert len(subnets) == len(rnns)

        self.blocks = len(subnets)
        self.seq_len = seq_len

        for index, (subnet, rnn) in enumerate(zip(subnets, rnns)):
            setattr(self, 'rnn' + str(self.blocks-index), rnn)
            setattr(self, 'stage' + str(self.blocks-index), subnet)

    def forward_by_stage(self, input_, state, subnet, rnn):
        input_, state_stage = rnn(input_, state, self.seq_len)
        batch_size, seq_number, input_channel, height, width = input_.size()
        input_ = torch.reshape(input_, (-1, input_channel, height, width))
        input_ = subnet(input_)
        input_ = torch.reshape(input_, (batch_size, seq_number, input_.shape[1], input_.size(2), input_.size(3)))

        return input_

        # input_: 5D S*B*I*H*W

    def forward(self, hidden_states):
        input_ = self.forward_by_stage(None, hidden_states[-1], getattr(self, 'stage3'), getattr(self, 'rnn3'))        
        for i in list(range(1, self.blocks))[::-1]:
            input_ = self.forward_by_stage(input_, hidden_states[i-1], getattr(self, 'stage' + str(i)),
                                                       getattr(self, 'rnn' + str(i)))
        return input_


class EF(nn.Module):
    def __init__(self, encoder, forecaster):
        super().__init__()
        self.encoder = encoder
        self.forecaster = forecaster

    def forward(self, input_):
        state = self.encoder(input_)
        output = self.forecaster(state)
        return output

def get_model(args):
    from src.operators.GRUcells import get_cells
    IN_LEN = args.I_nframes
    PRED_LEN = args.F_nframes
    encoder_elements, forecaster_elements = get_cells(args.model, args.dataset)
    encoder = Encoder(subnets=encoder_elements[0], rnns=encoder_elements[1], seq_len=IN_LEN)
    forecaster = Forecaster(subnets=forecaster_elements[0], rnns=forecaster_elements[1], seq_len=PRED_LEN)
    return EF(encoder, forecaster)