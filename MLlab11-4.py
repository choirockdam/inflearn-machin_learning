#Ensemble Layer를 이용하여 CNN구현
import tensorflow as tf
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data

tf.set_random_seed(777)
mnist= input_data.read_data_sets('MNIST_data', one_hot=True)

learning_rate = 0.001
training_epochs = 20
batch_size = 100

class Model:
    def __init__(self,sess,name):
        self.sess = sess
        self.name = name
        self._build_net()
    def _build_net(self):
        with tf.variable_scope(self.name):
            self.training = tf.placeholder(tf.bool)

            self.X = tf.placeholder(tf.float32,[None,784])
            X_img = tf.reshape(self.X, [-1,28,28,1])
            self.Y = tf.placeholder(tf.float32, [None, 10])

            conv1 = tf.layers.conv2d(X_img,filters=32,kernel_size=[3,3],padding="SAME",activation=tf.nn.relu)
            pool1 = tf.layers.max_pooling2d(conv1,pool_size=[2,2],strides=2,padding="SAME")
            dropout1 = tf.layers.dropout(pool1,rate=0.7,training=self.training)

            conv2 = tf.layers.conv2d(dropout1,filters=64,kernel_size=[3,3],padding="SAME",activation=tf.nn.relu)
            pool2 = tf.layers.max_pooling2d(conv2,pool_size=[2,2],strides=2,padding="SAME")
            dropout2 = tf.layers.dropout(pool2,rate=0.7,training=self.training)

            conv3 = tf.layers.conv2d(dropout2,filters=128, kernel_size=[3,3], padding='SAME', activation=tf.nn.relu)
            pool3 = tf.layers.max_pooling2d(conv3,pool_size=[2,2], strides=2, padding="SAME")
            dropout3 = tf.layers.dropout(pool3, rate=0.7, training=self.training)
            flat = tf.reshape(dropout3, [-1,128*4*4])

            dense4 = tf.layers.dense(flat,units=625,activation=tf.nn.relu)
            dropout4 = tf.layers.dropout(dense4, rate=0.5, training=self.training)

            self.logics = tf.layers.dense(dropout4,units=10)

        self.cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.logics, labels= self.Y))
        self.optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(self.cost)

        correct_prediction = tf.equal(tf.arg_max(self.logics,1),tf.arg_max(self.Y,1))
        self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    def train(self,x_data,y_data,training=True):
        return self.sess.run([self.cost,self.optimizer],feed_dict={self.X:x_data, self.Y:y_data, self.training:training})
    def predict(self,x_test, training=False):
        return self.sess.run(self.logics, feed_dict={self.X:x_test, self.training:training})
    def get_accuracy(self,x_test,y_test,training=False):
        return self.sess.run(self.accuracy, feed_dict={self.X:x_test, self.Y:y_test, self.training:training})

sess = tf.Session()
models = []
num_models = 2
for m in range(num_models):
    models.append(Model(sess, "model"+str(m)))
sess.run(tf.global_variables_initializer())
print('Learning Started')

for epoch in range(training_epochs):
    avg_cost_list = np.zeros(len(models))
    total_batch = int(mnist.train.num_examples / batch_size)
    for i in range(total_batch):
        batch_xs, batch_ys = mnist.train.next_batch(batch_size)

        for m_idx, m in enumerate(models):
            c, _ = m.train(batch_xs,batch_ys)
            avg_cost_list[m_idx] = avg_cost_list[m_idx] + c / total_batch

    print('Epoch: ', '%04d' %(epoch + 1), 'cost = ', avg_cost_list)

print('Learning Finished!')

test_size = len(mnist.test.labels)
predictions = np.zeros(test_size * 10).reshape(test_size,10)
for m_idx, m in enumerate(models):
    print(m_idx, 'Accuracy', m.get_accuracy(mnist.test.images, mnist.test.labels))
    p = m.predict(mnist.test.images)
    predictions = predictions + p

ensemble_correct_prediction = tf.equal(tf.arg_max(predictions, 1), tf.arg_max(mnist.test.labels,1))
ensemble_accuracy = tf.reduce_mean(tf.cast(ensemble_correct_prediction,tf.float32))
print('Ensemble accuracy : ', sess.run(ensemble_accuracy))