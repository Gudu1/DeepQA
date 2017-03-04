'''
Main Train Model Module
'''
import os
import time
import config
import functools
import itertools
import tensorflow as tf
import models.service as snap_model
from collections import namedtuple
from models.dual_encoder import dual_encoder_model
from tensorflow.contrib.learn.python.learn.metric_spec import MetricSpec

CONF = config.get_properties()

# Hyper parameters
# Model Parameters
tf.flags.DEFINE_integer(
    "vocab_size",
    int(CONF['hyparams']['vocab_size']),
    "The size of the vocabulary. Only change this if you changed the preprocessing")

# Model Parameters
tf.flags.DEFINE_integer("embedding_dim", int(
    CONF['hyparams']['embedding_dim']), "Dimensionality of the embeddings")
tf.flags.DEFINE_integer("rnn_dim", int(
    CONF['hyparams']['rnn_dim']), "Dimensionality of the RNN cell")
tf.flags.DEFINE_integer("max_context_len", int(
    CONF['hyparams']['max_context_len']), "Truncate contexts to this length")
tf.flags.DEFINE_integer("max_utterance_len", int(
    CONF['hyparams']['max_utterance_len']), "Truncate utterance to this length")

# Pre-trained embeddings
tf.flags.DEFINE_string("glove_path", CONF['hyparams'][
                       'glove_path'], "Path to pre-trained Glove vectors")
tf.flags.DEFINE_string("vocab_path", CONF['hyparams'][
                       'vocab_path'], "Path to vocabulary.txt file")

# Training Parameters
tf.flags.DEFINE_integer("train_steps", int(
    CONF['hyparams']['train_steps']), "Truncate utterance to this length")
tf.flags.DEFINE_float("learning_rate", float(
    CONF['hyparams']['learning_rate']), "Learning rate")
tf.flags.DEFINE_integer("batch_size", int(
    CONF['hyparams']['batch_size']), "Batch size during training")
tf.flags.DEFINE_integer("eval_batch_size", int(
    CONF['hyparams']['eval_batch_size']), "Batch size during evaluation")
tf.flags.DEFINE_string("optimizer", "Adam",
                       "Optimizer Name (Adam, Adagrad, etc)")
tf.flags.DEFINE_string("input_dir", CONF['hyparams']['input_dir'],
                       "Directory containing input data files 'train.tfrecords' and 'validation.tfrecords'")
tf.flags.DEFINE_string(
    "model_dir", None, "Directory to store model checkpoints (defaults to ./runs)")
tf.flags.DEFINE_integer(
    "num_epochs", int(CONF['hyparams']['num_epochs']), "Number of training Epochs. Defaults to indefinite.")
tf.flags.DEFINE_integer(
    "eval_every", int(CONF['hyparams']['eval_every']), "Evaluate after this many train steps")

FLAGS = tf.flags.FLAGS

HParams = namedtuple(
    "HParams",
    [
        "batch_size",
        "embedding_dim",
        "eval_batch_size",
        "learning_rate",
        "max_context_len",
        "max_utterance_len",
        "optimizer",
        "rnn_dim",
        "vocab_size",
        "glove_path",
        "vocab_path"
    ])

def create_hparams():
    return HParams(
        batch_size=FLAGS.batch_size,
        eval_batch_size=FLAGS.eval_batch_size,
        vocab_size=FLAGS.vocab_size,
        optimizer=FLAGS.optimizer,
        learning_rate=FLAGS.learning_rate,
        embedding_dim=FLAGS.embedding_dim,
        max_context_len=FLAGS.max_context_len,
        max_utterance_len=FLAGS.max_utterance_len,
        glove_path=FLAGS.glove_path,
        vocab_path=FLAGS.vocab_path,
        rnn_dim=FLAGS.rnn_dim)
# End Create hyper parameters

# Create Eval Metrics
def create_evaluation_metrics():
    eval_metrics = {}
    for k in [1, 2, 5]:
        eval_metrics["recall_at_%d" % k] = MetricSpec(metric_fn=functools.partial(
            tf.contrib.metrics.streaming_sparse_recall_at_k,
            k=k))
    return eval_metrics
# End Create Eval Metrics

# Inputs Definitions
def get_feature_columns(mode):
    TEXT_FEATURE_SIZE = int(CONF['hyparams']['text_feature_size'])
    feature_columns = []
    feature_columns.append(tf.contrib.layers.real_valued_column(
        column_name="context", dimension=TEXT_FEATURE_SIZE, dtype=tf.int64))
    feature_columns.append(tf.contrib.layers.real_valued_column(
        column_name="context_len", dimension=1, dtype=tf.int64))
    feature_columns.append(tf.contrib.layers.real_valued_column(
        column_name="utterance", dimension=TEXT_FEATURE_SIZE, dtype=tf.int64))
    feature_columns.append(tf.contrib.layers.real_valued_column(
        column_name="utterance_len", dimension=1, dtype=tf.int64))

    if mode == tf.contrib.learn.ModeKeys.TRAIN:
        # During training we have a label feature
        feature_columns.append(tf.contrib.layers.real_valued_column(
            column_name="label", dimension=1, dtype=tf.int64))

    if mode == tf.contrib.learn.ModeKeys.EVAL:
        # During evaluation we have distractors
        for i in range(9):
            feature_columns.append(tf.contrib.layers.real_valued_column(
                column_name="distractor_{}".format(i), dimension=TEXT_FEATURE_SIZE, dtype=tf.int64))
            feature_columns.append(tf.contrib.layers.real_valued_column(
                column_name="distractor_{}_len".format(i), dimension=1, dtype=tf.int64))

    return set(feature_columns)

def create_input_fn(mode, input_files, batch_size, num_epochs):
    def input_fn():
        features = tf.contrib.layers.create_feature_spec_for_parsing(
            get_feature_columns(mode))  # 通过parsing_ops函数renturn a dict mapping feature keys to FixedLenFeature or VarLenFeature values
                                        
        feature_map = tf.contrib.learn.io.read_batch_features(
            file_pattern=input_files,
            batch_size=batch_size,
            features=features,
            reader=tf.TFRecordReader,
            randomize_input=True,
            num_epochs=num_epochs,
            queue_capacity=200000 + batch_size * 10,
            name="read_batch_features_{}".format(mode))

        # This is an ugly hack because of a current bug in tf.learn
        # During evaluation TF tries to restore the epoch variable which isn't defined during training
        # So we define the variable manually here
        if mode == tf.contrib.learn.ModeKeys.TRAIN:
            tf.get_variable(
                "read_batch_features_eval/file_name_queue/limit_epochs/epochs",
                initializer=tf.constant(0, dtype=tf.int64))

        if mode == tf.contrib.learn.ModeKeys.TRAIN:
            target = feature_map.pop("label")
        else:
            # In evaluation we have 10 classes (utterances).
            # The first one (index 0) is always the correct one
            target = tf.zeros([batch_size, 1], dtype=tf.int64)
        print("feature_map{}".format(feature_map))
        print('target{}'.format(target))
        return feature_map, target
    return input_fn
# End Inputs Definitions

def main(unused_argv):
    '''
    Invoked by tensorflow framework
    http://eng.snaplingo.net/how-does-tf-app-run-work/
    '''
    TIMESTAMP = int(time.time())

    if FLAGS.model_dir:
        MODEL_DIR = FLAGS.model_dir
    else:
        MODEL_DIR = os.path.abspath(os.path.join("./runs", str(TIMESTAMP)))

    TRAIN_FILE = os.path.abspath(os.path.join(
        FLAGS.input_dir, "train.tfrecords"))
    VALIDATION_FILE = os.path.abspath(os.path.join(
        FLAGS.input_dir, "validation.tfrecords"))

    hparams = create_hparams()

    model_fn = snap_model.create_model_fn(
        hparams,
        model_impl=dual_encoder_model)

    estimator = tf.contrib.learn.Estimator(
        model_fn=model_fn,
        model_dir=MODEL_DIR,
        config=tf.contrib.learn.RunConfig())

    input_fn_train = create_input_fn(
        mode=tf.contrib.learn.ModeKeys.TRAIN,
        input_files=[TRAIN_FILE],
        batch_size=hparams.batch_size,
        num_epochs=FLAGS.num_epochs)

    input_fn_eval = create_input_fn(
        mode=tf.contrib.learn.ModeKeys.EVAL,
        input_files=[VALIDATION_FILE],
        batch_size=hparams.eval_batch_size,
        num_epochs=1)

    eval_metrics = create_evaluation_metrics()
    eval_monitor = tf.contrib.learn.monitors.ValidationMonitor(
        input_fn=input_fn_eval,
        every_n_steps=FLAGS.eval_every,
        metrics=eval_metrics)
    estimator.fit(input_fn=input_fn_train, steps=int(
        CONF['hyparams']['train_steps']), monitors=[eval_monitor])

if __name__ == "__main__":
    tf.logging.set_verbosity(int(CONF['log']['log_level']))
    tf.app.run()
