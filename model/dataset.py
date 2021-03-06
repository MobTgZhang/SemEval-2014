import csv
from tqdm import tqdm
import torch
import torch.utils.data

from .Constants import Constants
from .utils import map_label_to_target
class SICKDataset(torch.utils.data.Dataset):
    def __init__(self,vocabuary,seq_len,num_classes,filename):
        # foramt (sentA,sentB,score,sentiment_label)
        self.seq_len = seq_len
        self.vocabuary = vocabuary
        self.num_classes = num_classes
        self.read_file(filename)
    def read_file(self,filename):
        lsentences = []
        rsentences = []
        scores = []
        with open(filename,mode="r",encoding="utf-8") as f:
            reader = csv.reader(f,delimiter="\t")
            flag = False
            for row in reader:
                if not flag:
                    flag = True
                    continue
                lsent = row[1]
                rsent = row[2]
                score = float(row[3])
                lsentences.append(self.read_sentence(lsent))
                rsentences.append(self.read_sentence(rsent))
                dist_list = map_label_to_target(score,self.num_classes)
                scores.append(dist_list)
        self.lsentences = torch.LongTensor(lsentences,device='cpu')
        self.rsentences = torch.LongTensor(rsentences,device='cpu')
        self.scores_dist = torch.FloatTensor(scores,device='cpu')
    def read_sentence(self, line):
        indices = self.vocabuary.convertToIdx(line.split(), Constants.UNK_WORD,bosWord=Constants.BOS_WORD)
        while len(indices)<self.seq_len-1:
            indices += [Constants.PAD]
        indices += [Constants.EOS]
        if len(indices)>self.seq_len:
            raise ValueError("Sequence length should be resize:%d"%len(indices))
        return indices
    def __getitem__(self, item):
        return self.lsentences[item],self.rsentences[item],self.scores_dist[item]
    def __len__(self):
        return len(self.lsentences)
