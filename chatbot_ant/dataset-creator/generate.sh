python create_dataset.py "$@" --output 'train.csv' 'train'
python create_dataset.py "$@" --output 'test.csv' 'test'
python create_dataset.py "$@" --output 'valid.csv' 'valid'