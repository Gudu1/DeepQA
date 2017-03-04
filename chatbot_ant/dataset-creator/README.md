# Deep Learning Python Scripts

## Create dialogues and metadata

```
cd dataset-creator
sudo pip install MySQL-python jieba langid nltk
# Generate dialogues
cp config.sample.ini config.ini
python dialogues/selector.py
# Generate metadata
python dialogues/meta_data.py
```

Output:
check out **deeplearning/dialogues** and **deeplearning/meta**.

## Create csv files

### generate.sh:
#### DESCRIPTION:
Script that calls `create_dataset.py`. This is the script you should run in order to download the dataset. The parameters passed to this script will be passed to `create_dataset.py`. 
Example usage: `./generate.sh -t -s -l`.

### create_dataset.py:
#### DESCRIPTION:
Script for generation of train, test and valid datasets from SnapLingo Corpus 1 on 1 dialogs.
The script downloads 1on1 dialogs from internet and then it randomly samples all the datasets with positive and negative examples.

#### ARGUMENTS:
- `--seed`: seed for random number generator (default = 1234)
- `-o`, `--output`: output file for writing to csv (default = None)
- `-t`, `--tokenize`: tokenize the output (`nltk.word_tokenize`)
- `-s`, `--stem`: stem the output (`nltk.stem.SnowballStemmer`) - applied only when `-t` flag is present
- `-l`, `--lemmatize`: lemmatize the output (`nltk.stem.WorldNetLemmatizer`) - applied only when `-t` flag is present

*Note:* if both `-s` and `-l` are present, the stemmer is applied before the lemmatizer.

#### Subparsers:
`train`: train set generator
- `-p`: positive example probability, ie. the ratio of positive examples to total examples in the training set (default = 0.5)
- `-e`, `--examples`: number of training examples to generate. Note that this will generate slightly fewer examples than desired, as there is a 'post-processing' step that filters  (default = 1000000)

`valid`: validation set generator
- `-n`: number of distractor examples for each context (default = 9)

`test`: test set generator
- `-n`: number of distractor examples for each context (default = 9)