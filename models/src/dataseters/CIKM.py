import os
import numpy as np
import torch
from torch.utils.data import Dataset

class CIKMDataset(Dataset):
    ''' CIKM DATASET. '''
    def __init__(self, train=True, test=False, CIKMfolder='~/ssd/01_ty_research/08_CIKM', args=None, transform=None):
        super(CIKMDataset, self).__init__()
        CIKMfolder = os.path.expanduser(CIKMfolder)
        if train:
            self.filepath = [os.path.join(CIKMfolder, 'train', x) \
                for x in sorted(os.listdir(os.path.join(CIKMfolder, 'train')))]
        else:
            self.filepath = [os.path.join(CIKMfolder, 'testA', x) \
                for x in sorted(os.listdir(os.path.join(CIKMfolder, 'testA')))]
        if test:
            self.filepath = [os.path.join(CIKMfolder, 'testB', x) \
                for x in sorted(os.listdir(os.path.join(CIKMfolder, 'testB')))]
        if args is not None:
            np.random.seed(args.seed)
            randon_events = np.random.choice(len(self.filepath), len(self.filepath), replace=False)
        self.filepath = np.array(self.filepath)
        self.filepath = self.filepath[randon_events]
        self.transform = transform
        
    def __len__(self):
        return len(self.filepath)

    def __getitem__(self, idx):
        assert idx < self.__len__(), 'Index is out of the range of all data!'
        data = np.load(self.filepath[idx])[:,3]/256
        self.sample = {'inputs': data[:5], 'targets': data[5:]}

        if self.transform:
            self.sample = self.transform(self.sample)
        
        return self.sample

class ToTensor():
    def __call__(self, sample):
        return {'inputs': torch.from_numpy(sample['inputs']).unsqueeze(1),
                'targets': torch.from_numpy(sample['targets']).unsqueeze(1)}

class Normalize():
    pass