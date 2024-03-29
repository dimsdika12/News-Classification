# -*- coding: utf-8 -*-
"""News Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ngEbMPsSyO2pOnhyg49FqvCUU6YAcLnP

The dataset can be accessed [from this source](https://www.kaggle.com/datasets/kishanyadav/inshort-news?select=inshort_news_data-1.csv).

Import Library
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import Callback

"""Import Dataset"""

url = 'https://raw.githubusercontent.com/dimsdika12/News-Classification/main/dataset/inshort_news_data-1.csv'
df = pd.read_csv(url)
df.head()

"""Delete unused columns"""

df.drop(['Unnamed: 0', 'news_headline'], axis=1, inplace=True)
df.head()

"""Count the number of null values in each column"""

df.isnull().sum()

"""distribution of genres"""

news_category_counts = df["news_category"].value_counts()
plt.figure(figsize=(8, 8))
news_category_counts.plot(kind="pie", autopct="%.2f%%")
plt.title("Distribution of news_category")
plt.show()

"""Delete some genres that will not be used (used top 4)"""

news_category_to_drop = ['automobile', 'science', 'politics']
df.drop(df[df['news_category'].isin(news_category_to_drop)].index, axis=0, inplace=True)

"""Convert categorical data into a numerical representation. For the 'genre' column, use One-hot encoding"""

category = pd.get_dummies(df.news_category)
df_new = pd.concat([df, category], axis=1)
df_new = df_new.drop(columns='news_category')
df_new

"""convert the values from the dataframe into the numpy array data type"""

article = df_new['news_article'].values
label = df_new[['entertainment','sports','technology','world']].values

"""Split dataset for training and data for testing."""

article_train, article_test, label_train, label_test = train_test_split(article, label, test_size=0.2)

print("Number of data entries in article_train:", article_train.shape[0])
print("Number of data entries in article_test:", article_test.shape[0])
print("Number of data entries in label_train:", label_train.shape[0])
print("Number of data entries in label_test:", label_test.shape[0])

"""aplly NLTK"""

stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    tokenizer = RegexpTokenizer(r"\w+")
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words and w.isalpha()]
    return ' '.join(filtered_sentence)

article_train = [preprocess_text(text) for text in article_train]
article_test = [preprocess_text(text) for text in article_test]

"""Initializes a tokenizer, fits it on training and test synopses, converts text to sequences, and then pads the sequences for further processing."""

tokenizer = Tokenizer(num_words=5000, oov_token='<oov>')
tokenizer.fit_on_texts(article_train)
#tokenizer.fit_on_texts(article_test)

training_sequences = tokenizer.texts_to_sequences(article_train)
test_sequences = tokenizer.texts_to_sequences(article_test)

maxlen = 500
padded_training = pad_sequences(training_sequences, maxlen=maxlen, truncating='post')
padded_test = pad_sequences(test_sequences, maxlen=maxlen, truncating='post')

"""Create model"""

import tensorflow as tf
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=5000, output_dim=16),
    tf.keras.layers.LSTM(128),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(4, activation='softmax')
])
model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])

"""train model"""

class MinimumAccuracyCallback(Callback):
    def on_epoch_end(self, epoch, logs={}):
      if(logs.get('accuracy')>0.90 and logs.get('val_accuracy')>0.90):
        print("\nReached minimum accuracy of 90% on both training and validation sets!")
        self.model.stop_training = True
callback = MinimumAccuracyCallback()
history = model.fit(padded_training, label_train, epochs=50,
                    validation_data=(padded_test, label_test), verbose=2, callbacks=[callback])

"""plot loss and accuracy"""

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Akurasi Model')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.show()