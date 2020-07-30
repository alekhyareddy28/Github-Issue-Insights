import pandas as pd
from sklearn.neural_network import MLPRegressor
from joblib import dump, load
from sklearn.preprocessing import normalize
import gensim
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk import word_tokenize
import numpy as np
import string
import time
from sklearn.metrics.pairwise import cosine_similarity

def stemming_tokenizer(text):
    stemmer = PorterStemmer()
    temp = text.replace("\\r", " ")
    temp = temp.replace("\\n", " ")
    return [stemmer.stem(w) for w in word_tokenize(temp)]

def load_model(filename='default.joblib'):
    return load(filename)

issue_title_mean = load_model('..\\Notebooks\\issue_title_mean.joblib')
issue_description_mean = load_model('..\\Notebooks\\issue_description_mean.joblib')
issue_label_mean = load_model('..\\Notebooks\\issue_label_mean.joblib')
pr_title_mean = load_model('..\\Notebooks\\pr_title_mean.joblib')
pr_description_mean = load_model('..\\Notebooks\\pr_description_mean.joblib')

def input_feature_extraction(x_title, x_desc, x_label):
    x1 = np.array(x_title)
    x2 = np.array(x_desc)
    x3 = np.array(x_label)
    a = 10
    b = 1
    c = 1
    return a*normalize(x1 - issue_title_mean) + b*normalize(x2 - issue_description_mean) + c*normalize(x3 - issue_label_mean)

def output_feature_extraction(y_title, y_desc):
    y1 = y_title
    y2 = y_desc
    a = 10
    b = 1
    return a*normalize(y1 - pr_title_mean) + b*normalize(y2 - pr_description_mean)

def predict_and_get_cosine_sim(x, y, clf):
    y_pred = clf.predict(x)
    return cosine_similarity(y_pred, y)

# load word2vec model
print("Loading word2vec model")
model = load_model('..\\Notebooks\\word2vec.joblib')
print("Loading neural network model")
modelFileName = "..\\Notebooks\\testmodel2.joblib"
classifier = load_model(modelFileName)
stop_words = stopwords.words('english')+list(string.punctuation)
stemmed_stop_words = stemming_tokenizer(" ".join(stop_words))

def get_vector(text, debug=False):
    vec = np.zeros(300)
    found_count = 0
    total_count = 0
    for word in stemming_tokenizer(text):
        if word.lower() in stemmed_stop_words:
            continue
        total_count += 1
        if word.lower() in model:
            vec = vec + model[word.lower()]
            found_count += 1
    if debug:
        print(found_count, total_count)
    return vec

def get_top_k_predictions(x, y, clf, k):
    cosineMat = predict_and_get_cosine_sim(x, y, clf)
    print(cosineMat)
    # Sort in descending order
    return np.argsort(-1*cosineMat)[:, :k]

def get_recommended_pull_requests(issue_data, pr_data):
    # Create word vectors from issue data
    X_issue_title_wordvec = [get_vector(issue_data[0])]
    X_issue_description_wordvec = [get_vector(issue_data[1])]
    X_issue_label_wordvec = [get_vector(issue_data[2])]


    # Create word vectors from PR data
    Y_pr_title_wordvec = []
    Y_pr_description_wordvec = []
    for pr in pr_data:
        Y_pr_title_wordvec.append(get_vector(pr.title))
        Y_pr_description_wordvec.append(get_vector(pr.body))
    
    # Skip if there are no pull requests
    if len(Y_pr_title_wordvec) == 0:
        return pr_data

    # Make prediction
    y_pred = get_top_k_predictions(input_feature_extraction(X_issue_title_wordvec, X_issue_description_wordvec, X_issue_label_wordvec), output_feature_extraction(Y_pr_title_wordvec, Y_pr_description_wordvec), classifier, 3)

    # Return subset of PRs
    pr_list = [pr for pr in pr_data]
    
    return [pr_list[i] for i in y_pred[0]]