import tensorflow as tf
import collections
import jieba
import pickle
class Seq2seq_model:
    def __init__(self, size_layer, num_layers, embedded_size,
                 from_dict_size, to_dict_size, batch_size,
                 grad_clip=5.0, beam_width=5, force_teaching_ratio=0.5):
        self.GO = 0
        self.PAD = 1
        self.EOS = 2
        self.UNK = 3
        def cells(size, reuse=False):
            return tf.nn.rnn_cell.GRUCell(size, reuse=reuse)

        self.X = tf.placeholder(tf.int32, [None, None])
        self.Y = tf.placeholder(tf.int32, [None, None])
        self.X_seq_len = tf.count_nonzero(self.X, 1, dtype=tf.int32)
        self.Y_seq_len = tf.count_nonzero(self.Y, 1, dtype=tf.int32)
        batch_size = tf.shape(self.X)[0]

        encoder_embeddings = tf.Variable(tf.random_uniform([from_dict_size, embedded_size], -1, 1))
        decoder_embeddings = tf.Variable(tf.random_uniform([to_dict_size, embedded_size], -1, 1))
        self.encoder_out = tf.nn.embedding_lookup(encoder_embeddings, self.X)

        for n in range(num_layers):
            (out_fw, out_bw), (state_fw, state_bw) = tf.nn.bidirectional_dynamic_rnn(
                cell_fw=cells(size_layer // 2),
                cell_bw=cells(size_layer // 2),
                inputs=self.encoder_out,
                sequence_length=self.X_seq_len,
                dtype=tf.float32,
                scope='bidirectional_rnn_%d' % (n))
            encoder_embedded = tf.concat((out_fw, out_bw), 2)

        bi_state = tf.concat((state_fw, state_bw), -1)
        encoder_state = tuple([bi_state] * num_layers)
        encoder_state = tuple(encoder_state[-1] for _ in range(num_layers))

        with tf.variable_scope('decode'):
            attention_mechanism = tf.contrib.seq2seq.LuongAttention(
                num_units=size_layer,
                memory=self.encoder_out,
                memory_sequence_length=self.X_seq_len)
            decoder_cell = tf.contrib.seq2seq.AttentionWrapper(
                cell=tf.nn.rnn_cell.MultiRNNCell([cells(size_layer) for _ in range(num_layers)]),
                attention_mechanism=attention_mechanism,
                attention_layer_size=size_layer)
            main = tf.strided_slice(self.Y, [0, 0], [batch_size, -1], [1, 1])
            decoder_input = tf.concat([tf.fill([batch_size, 1], self.GO), main], 1)
            training_helper = tf.contrib.seq2seq.ScheduledEmbeddingTrainingHelper(
                inputs=tf.nn.embedding_lookup(decoder_embeddings, decoder_input),
                sequence_length=self.Y_seq_len,
                embedding=decoder_embeddings,
                sampling_probability=1 - force_teaching_ratio,
                time_major=False)
            training_decoder = tf.contrib.seq2seq.BasicDecoder(
                cell=decoder_cell,
                helper=training_helper,
                initial_state=decoder_cell.zero_state(batch_size, tf.float32).clone(cell_state=encoder_state),
                output_layer=tf.layers.Dense(to_dict_size))
            training_decoder_output, _, _ = tf.contrib.seq2seq.dynamic_decode(
                decoder=training_decoder,
                impute_finished=True,
                maximum_iterations=tf.reduce_max(self.Y_seq_len))
            self.training_logits = training_decoder_output.rnn_output

        with tf.variable_scope('decode', reuse=True):
            encoder_out_tiled = tf.contrib.seq2seq.tile_batch(self.encoder_out, beam_width)
            encoder_state_tiled = tf.contrib.seq2seq.tile_batch(encoder_state, beam_width)
            X_seq_len_tiled = tf.contrib.seq2seq.tile_batch(self.X_seq_len, beam_width)
            attention_mechanism = tf.contrib.seq2seq.LuongAttention(
                num_units=size_layer,
                memory=encoder_out_tiled,
                memory_sequence_length=X_seq_len_tiled)
            decoder_cell = tf.contrib.seq2seq.AttentionWrapper(
                cell=tf.nn.rnn_cell.MultiRNNCell([cells(size_layer, reuse=True) for _ in range(num_layers)]),
                attention_mechanism=attention_mechanism,
                attention_layer_size=size_layer)
            predicting_decoder = tf.contrib.seq2seq.BeamSearchDecoder(
                cell=decoder_cell,
                embedding=decoder_embeddings,
                start_tokens=tf.tile(tf.constant([self.GO], dtype=tf.int32), [batch_size]),
                end_token=self.EOS,
                initial_state=decoder_cell.zero_state(batch_size * beam_width, tf.float32).clone(
                    cell_state=encoder_state_tiled),
                beam_width=beam_width,
                output_layer=tf.layers.Dense(to_dict_size, _reuse=True),
                length_penalty_weight=0.0)
            predicting_decoder_output, _, _ = tf.contrib.seq2seq.dynamic_decode(
                decoder=predicting_decoder,
                impute_finished=False,
                maximum_iterations=2 * tf.reduce_max(self.X_seq_len))
            self.predicting_ids = predicting_decoder_output.predicted_ids[:, :, 0]

        masks = tf.sequence_mask(self.Y_seq_len, tf.reduce_max(self.Y_seq_len), dtype=tf.float32)
        self.cost = tf.contrib.seq2seq.sequence_loss(logits=self.training_logits,
                                                     targets=self.Y,
                                                     weights=masks)
        self.optimizer = tf.train.AdamOptimizer(0.001).minimize(self.cost)
        y_t = tf.argmax(self.training_logits, axis=2)
        y_t = tf.cast(y_t, tf.int32)
        self.prediction = tf.boolean_mask(y_t, masks)
        mask_label = tf.boolean_mask(self.Y, masks)
        correct_pred = tf.equal(self.prediction, mask_label)
        correct_index = tf.cast(correct_pred, tf.float32)
        self.accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

class Seq2seq():
    def __init__(self):
        self.GO = 0
        self.PAD = 1
        self.EOS = 2
        self.UNK = 3
        with open('../data/seq2seq/dict_q.pkl', 'rb') as f:
            self.q_dict = pickle.load(f)
        with open('../data/seq2seq/rev_dict_a.pkl', 'rb') as f:
            self.a_rev_dict = pickle.load(f)
        tf.reset_default_graph()
        self.sess = tf.InteractiveSession()
        self.model = Seq2seq_model(128, 2, 128, len(self.q_dict),
                len(self.a_rev_dict), 128)
        saver = tf.train.Saver()
        saver.restore(self.sess, '../data/seq2seq/seq2seq')

    def build_dataset(self,words, n_words, atleast=1):
        count = [['GO', 0], ['PAD', 1], ['EOS', 2], ['UNK', 3]]
        counter = collections.Counter(words).most_common(n_words)
        counter = [i for i in counter if i[1] >= atleast]
        count.extend(counter)
        dictionary = dict()
        for word, _ in count:
            dictionary[word] = len(dictionary)
        data = list()
        unk_count = 0
        for word in words:
            index = dictionary.get(word, 0)
            if index == 0:
                unk_count += 1
            data.append(index)
        count[0][1] = unk_count
        reversed_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
        return dictionary, reversed_dictionary

    def pad_sentence(self,sentences, length=50):
        padded_seqs = []
        for sentence in sentences:
            if len(sentence) >= length:
                padded_seqs.append(sentence[:length])
            else:
                padded_seqs.append(sentence + [self.PAD] * (length - len(sentence)))
        return padded_seqs

    def predict(self,sent):
        ints = []
        print(jieba.lcut(sent))
        for k in jieba.cut(sent):
            if k == '':continue
            ints.append(self.q_dict.get(k, self.UNK))
        x = [ints]
        x = self.pad_sentence(x)
        predicted = self.sess.run([self.model.predicting_ids],
                             feed_dict={self.model.X: x})
        result = ''.join([self.a_rev_dict[n] for n in predicted[0][0] if n not in[0,1,2,3]])
        return result