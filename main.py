import pandas as pd
import warnings


from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from keras import layers, models as mdl, optimizers

from sklearn import metrics, preprocessing

from classes.data_exploring import ExploringData

warnings.filterwarnings("ignore", category=DeprecationWarning)
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC, LinearSVR, LinearSVC
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from classes import data_cleaning as dataclean
# resources:
# https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html
# http://cmdlinetips.com/2018/11/string-manipulations-in-pandas/
# w3schools.com/python
# https://www.analyticsvidhya.com/blog/2017/06/word-embeddings-count-word2veec/


#

train = pd.read_csv("data/dataset_1/train.csv", header='infer', index_col=None)
# test = pd.read_csv("data/dataset_1/test.csv", header='infer', index_col=None)

#train = pd.read_csv("data/dataset_2/train.csv", header='infer',index_col=None)
#test = pd.read_csv("data/dataset_2/test.csv", delimiter=None, header='infer', names=None, index_col=None, encoding='latin-1')

#preprocessing

#train = preproc.clean_data(train,"SentimentText")
#dtexplr.explore_non_racist_sexist_tweets(train,"SentimentText","Sentiment")
#dtexplr.explore_hashtags(train,"SentimentText","Sentiment")



def startTraining(train,train_tweet,train_label, dataexplore=False, storemodel=False):
    if dataexplore:
        exp1= ExploringData(train,train_tweet,train_label)
        exp1.runall()
    #clean data
    train = dataclean.clean_data(train, train_tweet)

    # splitting data into training and validation set
    xtrain, xvalid, ytrain, yvalid = train_test_split(train[train_tweet], train[train_label], random_state=0,
                                                      test_size=0.2)
    # label encode the target variable
    encoder = preprocessing.LabelEncoder()
    ytrain = encoder.fit_transform(ytrain)
    yvalid = encoder.fit_transform(yvalid)
    # START OF COUNT VECTORS AS FEATURES
    # create a count vectorizer object and transform the training and validation data using count vectorizer object
    count_vect = CountVectorizer(analyzer='word', token_pattern=r'\w{1,}')
    count_vect.fit(train[train_tweet])
    xtrain_count =  count_vect.transform(xtrain)
    xvalid_count =  count_vect.transform(xvalid)
    # END OF COUNT VECTORS AS FEATURES

    # START OF TF-IDF VECTORS AS FEATURES
    # word level tf-idf
    tfidf_vect = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', max_features=2500)
    tfidf_vect.fit(train[train_tweet])
    xtrain_tfidf = tfidf_vect.transform(xtrain)
    xvalid_tfidf = tfidf_vect.transform(xvalid)
    # ngram level tf-idf
    tfidf_vect_ngram = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', ngram_range=(2, 3), max_features=2500)
    tfidf_vect_ngram.fit(train[train_tweet])
    xtrain_tfidf_ngram = tfidf_vect_ngram.transform(xtrain)
    xvalid_tfidf_ngram = tfidf_vect_ngram.transform(xvalid)
    # characters level tf-idf
    tfidf_vect_ngram_chars = TfidfVectorizer(analyzer='char', token_pattern=r'\w{1,}', ngram_range=(2, 3),
                                             max_features=2500)
    tfidf_vect_ngram_chars.fit(train[train_tweet])
    xtrain_tfidf_ngram_chars = tfidf_vect_ngram_chars.transform(xtrain)
    xvalid_tfidf_ngram_chars = tfidf_vect_ngram_chars.transform(xvalid)
    # END OF TF-IDF VECTORS AS FEATURES

    # START OF BAG OF WORDS FEATURE
    train_bow = CountVectorizer(max_features=1000, lowercase=True, ngram_range=(1,1),analyzer = "word")
    train_bow.fit(train[train_tweet])
    xtrain_bow = train_bow.transform(xtrain)
    xvalid_bow = train_bow.transform(xvalid)
    # END OF BAG OF WORDS FEATURE

    #START OF WORD EMBEDDINGS FEATURE

    #END OF WORD EMBEDDINGS FEATURE

    def train_model(classifier, feature_vector_train, label, feature_vector_valid, is_neural_net=False):
        # fit the training dataset on the classifier
        classifier.fit(feature_vector_train, label)

        # predict the labels on validation dataset
        predictions = classifier.predict(feature_vector_valid)

        if is_neural_net:
            predictions = predictions.argmax(axis=-1)

        return metrics.accuracy_score(predictions, yvalid)


    def create_model_architecture(input_size):
        # create input layer
        input_layer = layers.Input((input_size,), sparse=True)

        # create hidden layer
        hidden_layer = layers.Dense(100, activation="relu")(input_layer)

        # create output layer
        output_layer = layers.Dense(1, activation="sigmoid")(hidden_layer)

        classifier = mdl.Model(inputs=input_layer, outputs=output_layer)
        classifier.compile(optimizer=optimizers.Adam(), loss='binary_crossentropy')
        return classifier

    # def create_cnn():
    #     # Add an Input Layer
    #     input_layer = layers.Input((70,))
    #
    #     # Add the word embedding Layer
    #     embedding_layer = layers.Embedding(len(word_index) + 1, 300, weights=[embedding_matrix], trainable=False)(
    #         input_layer)
    #     embedding_layer = layers.SpatialDropout1D(0.3)(embedding_layer)
    #
    #     # Add the convolutional Layer
    #     conv_layer = layers.Convolution1D(100, 3, activation="relu")(embedding_layer)
    #
    #     # Add the pooling Layer
    #     pooling_layer = layers.GlobalMaxPool1D()(conv_layer)
    #
    #     # Add the output Layers
    #     output_layer1 = layers.Dense(50, activation="relu")(pooling_layer)
    #     output_layer1 = layers.Dropout(0.25)(output_layer1)
    #     output_layer2 = layers.Dense(1, activation="sigmoid")(output_layer1)
    #
    #     # Compile the model
    #     model = mdl.Model(inputs=input_layer, outputs=output_layer2)
    #     model.compile(optimizer=optimizers.Adam(), loss='binary_crossentropy')
    #
    #     return model

    # START OF TRAINING WITH TRADITIONAL MACHINE LEARNING METHODS
    models = [MultinomialNB(),LogisticRegression(),SVC(gamma='auto'), LinearSVC(),
              SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, random_state=42, max_iter=5, tol=None),
              KNeighborsClassifier(),RandomForestClassifier(),XGBClassifier(),
              MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)]

    entries = []
    for model in models:
        model_name = model.__class__.__name__
        # Model on Count Vectors
        cv_accuracy = train_model(model, xtrain_count, ytrain, xvalid_count)

        # Model on Word Level TF IDF Vectors
        tfidf_word_accuracy = train_model(model, xtrain_tfidf, ytrain, xvalid_tfidf)

        # Model on Ngram Level TF IDF Vectors
        tfidf_ngram_accuracy = train_model(model, xtrain_tfidf_ngram, ytrain, xvalid_tfidf_ngram)

        # Model on Character Level TF IDF Vectors
        tfidf_character_accuracy = train_model(model, xtrain_tfidf_ngram_chars, ytrain, xvalid_tfidf_ngram_chars)

        # Model on  bag of words
        bow_accuracy = train_model(model, xtrain_bow, ytrain, xvalid_bow)
        entries.append((model_name, cv_accuracy,tfidf_word_accuracy,tfidf_ngram_accuracy,tfidf_character_accuracy,bow_accuracy))

        cv_df = pd.DataFrame(entries, columns=['model_name', 'cvo', 'tfidf_word_lvl','tfidf_ngram','tfidf_character_lvl','bow'])
    print(cv_df)


    # END OF TRAINING WITH TRADITIONAL MACHINE LEARNING METHODS

    # START TRAINING WITH SHALLOW NEURAL NETWORKS
    classifier = create_model_architecture(xtrain_tfidf_ngram.shape[1])
    accuracy1 = train_model(classifier, xtrain_tfidf_ngram, ytrain, xvalid_tfidf_ngram, is_neural_net=True)
    print("NN, Ngram Level TF IDF Vectors", accuracy1)
    # END TRAINING WITH SHALLOW NEURAL NETWORKS

    # START TRAINING WITH SHALLOW NEURAL NETWORKS
    classifier = create_model_architecture(xtrain_bow.shape[1])
    accuracy2 = train_model(classifier, xtrain_bow, ytrain, xvalid_bow, is_neural_net=True)
    print("NN, bow", accuracy2)
    # END TRAINING WITH SHALLOW NEURAL NETWORKS

    #START TRAINING WITH DEEP NEURAL NETWORKS

    #END TRAINING WITH DEEP NEURAL NETWORKS

#startTraining(train,"SentimentText","Sentiment")
startTraining(train,"tweet","label")
exit(0)