# Language-Identification-with-Curriculum-Learning

This model adds a Curriculum learning module to the model XSA, so that in the whole training process of the model.<br>
In the whole training process, our model gradually learns from easy samples to difficult samples. <br>
Using this method, we can get better results in the noisy test set without increasing the number of training data sets in the whole training process.<br>
The whole training process is divided into seven stages. The later stage contains more noisy data sets and the larger SNR.

When use Curriculum leanring, although noisy data sets are used, the amount of data sent into the model each epoch is always the same as the number of utterances in the original clean data set, but data sets with different signal-to-noise ratios will be included in different stages.

Before running this model, you need to execute the commands of data preparation and noise adding in model [XSA](https://github.com/zjc6666/Language-Identification).
## 
