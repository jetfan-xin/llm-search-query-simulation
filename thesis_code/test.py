from bert_score import BERTScorer
import torch
scorer = BERTScorer(model_type='bert-base-chinese', lang="zh", batch_size=1,
                            device='cuda' if torch.cuda.is_available() else 'cpu')
q1 = '解释 环境 生活 很感兴趣 实践 生活'
q2 = '持续 积极 搜索 环保 提供'
print(scorer.score([q1], [q2])[-1].item())
print(scorer.score([q2], [q1])[-1].item())