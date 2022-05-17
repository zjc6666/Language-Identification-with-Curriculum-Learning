# Language-Identification-with-Curriculum-Learning

This model adds a Curriculum learning module to the model XSA, so that in the whole training process of the model.<br>
In the whole training process, our model gradually learns from easy samples to difficult samples. <br>
Using this method, we can get better results in the noisy test set without increasing the number of training data sets in the whole training process.<br>
The whole training process is divided into seven stages. The later stage contains more noisy data sets and the larger SNR.

When use Curriculum leanring, although noisy data sets are used, the amount of data sent into the model each epoch is always the same as the number of utterances in the original clean data set, but data sets with different signal-to-noise ratios will be included in different stages.

Before running this model, you need to execute the commands of data preparation and noise adding in model [XSA](https://github.com/zjc6666/Language-Identification).
## Extractor noise data fearure
We first need to extract features from the noisy training set, then all training data sets are integrated.
```
python3 process_lre_data.py
utils/combine_data.sh data-16k/lre17_train_5th data-16k/lre17_train data-16k/lre17_train_5_snrs data-16k/lre17_train_10_snrs data-16k/lre17_train_15_snrs data-16k/lre17_train_20_snrs
cat data-16k/lre17_train_5_snrs/wav2vec_pretrained_model.txt data-16k/lre17_train_10_snrs/wav2vec_pretrained_model.txt data-16k/lre17_train_15_snrs/wav2vec_pretrained_model.txt data-16k/lre17_train_20_snrs/wav2vec_pretrained_model.txt data-16k/lre17_train/wav2vec_pretrained_model.txt > data-16k/lre17_train_5th/wav2vec_pretrained_model.txt
mkdir data-16k/lre17_train_5th/wav2vec_pretrained_model_16_layer
cat data-16k/lre17_train_5_snrs/wav2vec_pretrained_model_16_layer/feats.scp data-16k/lre17_train_10_snrs/wav2vec_pretrained_model_16_layer/feats.scp data-16k/lre17_train_15_snrs/wav2vec_pretrained_model_16_layer/feats.scp data-16k/lre17_train_20_snrs/wav2vec_pretrained_model_16_layer/feats.scp data-16k/lre17_train/wav2vec_pretrained_model_16_layer/feats.scp > data-16k/lre17_train_5th/wav2vec_pretrained_model_16_layer/feats.scp
mv data-16k/lre17_train_5th/wav2vec_pretrained_model.txt data-16k/lre17_train_5th/feats.scp
utils/fix_data_dir.sh data-16k/lre17_train_5th
mv data-16k/lre17_train_5th/feats.scp data-16k/lre17_train_5th/wav2vec_pretrained_model.txt
cp data-16k/lre17_train_5th/{utt2spk,utt2lang,wav.scp} data-16k/lre17_train_5th/wav2vec_pretrained_model_16_layer
utils/fix_data_dir.sh data-16k/lre17_train_5th/wav2vec_pretrained_model_16_layer
```
