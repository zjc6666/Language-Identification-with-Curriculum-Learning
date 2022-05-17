from transformer import *
from pooling_layers import *


class X_Transformer_E2E_LID(nn.Module):
    def __init__(self, input_dim, feat_dim,
                 d_k, d_v, d_ff, n_heads=4,
                 dropout=0.1, n_lang=3, max_seq_len=10000):
        super(X_Transformer_E2E_LID, self).__init__()
        self.input_dim = input_dim
        self.feat_dim = feat_dim
        self.dropout = nn.Dropout(p=dropout)
        # self.tdnn1 = nn.Conv1d(in_channels=input_dim, out_channels=512, kernel_size=5, dilation=1)
        self.tdnn1 = nn.Conv1d(in_channels=input_dim, out_channels=512, kernel_size=3)
        self.bn1 = nn.BatchNorm1d(512, momentum=0.1, affine=False)
        self.tdnn2 = nn.Conv1d(in_channels=512, out_channels=512, kernel_size=3)
        # self.tdnn2 = nn.Conv1d(in_channels=512, out_channels=512, kernel_size=5, dilation=2)
        self.bn2 = nn.BatchNorm1d(512, momentum=0.1, affine=False)
        self.tdnn3 = nn.Conv1d(in_channels=512, out_channels=512, kernel_size=1)
        # self.tdnn3 = nn.Conv1d(in_channels=512, out_channels=512, kernel_size=1, dilation=1)
        self.bn3 = nn.BatchNorm1d(512, momentum=0.1, affine=False)
        self.fc_xv = nn.Linear(1024, feat_dim)

        self.layernorm1 = LayerNorm(feat_dim)
        self.pos_encoding = PositionalEncoding(max_seq_len=max_seq_len, features_dim=feat_dim)
        self.layernorm2 = LayerNorm(feat_dim)
        self.d_model = feat_dim * n_heads
        self.n_heads = n_heads
        self.attention_block1 = EncoderBlock(self.d_model, d_k, d_v, d_ff, n_heads, dropout=dropout)
        self.attention_block2 = EncoderBlock(self.d_model, d_k, d_v, d_ff, n_heads, dropout=dropout)

        self.fc1 = nn.Linear(self.d_model * 2, self.d_model)
        self.fc2 = nn.Linear(self.d_model, self.d_model)
        self.fc3 = nn.Linear(self.d_model, n_lang)

    def mean_std_pooling(self, x, batchsize, seq_lens, mask_mean, weight_mean, mask_std, weight_unb):
        """

        :param x: expect the x is of shape [Batchsize, seq_len, feature_dim]

        :param batchsize: in you script this should be len(seq_lens), namely the number of samples
        :param seq_lens: a tuple of sequence lengths
        :param weight: remove zero paddings when computing means
        :param mask_std: remove zero paddings when computing std
        :param weight_unb: do unbaised estimation, then the results are the same as x.std for fixed chunks
        :return: concatenation of means and stds
        """
        max_len = seq_lens[0]
        feat_dim = x.size(-1)
        if mask_mean is not None:
            print( mask_mean.size() ," == ",x.size())
            assert mask_mean.size() == x.size()
            x.masked_fill_(mask_mean, 0)
        correct_mean = x.mean(dim=1).transpose(0, 1) * weight_mean
        correct_mean = correct_mean.transpose(0, 1)
        center_seq = x - correct_mean.repeat(1, 1, max_len).view(batchsize, -1, feat_dim)
        variance = torch.mean(torch.mul(torch.abs(center_seq) ** 2, mask_std), dim=1).transpose(0,1) \
                   * weight_unb * weight_mean
        std = torch.sqrt(variance.transpose(0, 1))
        return torch.cat((correct_mean, std), dim=1)

    def forward(self, x, seq_len, mean_mask_=None, weight_mean=None, std_mask_=None, weight_unbaised=None,
                atten_mask=None, eps=1e-5):
        batch_size = x.size(0)
        T_len = x.size(1)
        x = self.dropout(x)
        x = x.view(batch_size * T_len, -1, self.input_dim).transpose(-1, -2)
        x = self.bn1(F.relu(self.tdnn1(x)))
        x = self.bn2(F.relu(self.tdnn2(x)))
        x = self.bn3(F.relu(self.tdnn3(x)))

        if self.training:
            shape = x.size()
            noise = torch.Tensor(shape)
            noise = noise.type_as(x)
            torch.randn(shape, out=noise)
            x += noise * eps

        stats = torch.cat((x.mean(dim=2), x.std(dim=2)), dim=1)
        embedding = self.fc_xv(stats)
        embedding = embedding.view(batch_size, T_len, self.feat_dim)
        output = self.layernorm1(embedding)
        output = self.pos_encoding(output, seq_len)
        output = self.layernorm2(output)
        output = output.unsqueeze(1).repeat(1, self.n_heads, 1, 1)
        output = output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        output, _ = self.attention_block1(output, atten_mask)
        output, _ = self.attention_block2(output, atten_mask)
        if std_mask_ is not None:
            stats = self.mean_std_pooling(output, batch_size, seq_len, mean_mask_, weight_mean,
                                          std_mask_, weight_unbaised)
        else:
            stats = torch.cat((output.mean(dim=1), output.std(dim=1)), dim=1)

        output = F.relu(self.fc1(stats))
        output = F.relu(self.fc2(output))
        output = self.fc3(output)
        return output
