from django.shortcuts import render
from nltk.tokenize import regexp_tokenize
from nltk.tag import HiddenMarkovModelTrainer
from nltk.probability import LaplaceProbDist
from nltk.util import unique_list
import pickle
from django.conf import settings
import json
import codecs
import operator
import ast
import random

def get_random_address():
    with open(settings.BASE_DIR+"/data/raw.pkl", 'rb') as handle:
        raw = pickle.load(handle)
    if len(raw):
        a = raw.pop(random.randrange(len(raw)))
        with open(settings.BASE_DIR+"/data/raw.pkl", 'wb') as handle:
            pickle.dump(raw, handle)
        return a.decode()
    else:
        return "АДРЕСА КОНЧИЛИСЬ("

def corpus(request):
    with open(settings.BASE_DIR+"/data/corpus.pkl", 'rb') as handle:
        corpus = pickle.load(handle)

    if request.method == "POST":
        #import ipdb; ipdb.set_trace()
        if request.POST.get("tokens") and request.POST.get("true_index"):
            true_index = int(request.POST.get("true_index"))
            tokens = ast.literal_eval(request.POST.get("tokens"))
            tagged = []
            i = 1
            for item in tokens:
                tagged.append((item,request.POST.get("token_"+str(i))))
                i += 1
            del(corpus[true_index])
            corpus.append(tagged)
            with open(settings.BASE_DIR+"/data/corpus.pkl", 'wb') as handle:
                pickle.dump(corpus, handle)
            tag_set = unique_list(tag for sent in corpus for (word,tag) in sent)
            symbols = unique_list(word for sent in corpus for (word,tag) in sent)
            trainer = HiddenMarkovModelTrainer(tag_set, symbols)
            hmm = trainer.train_supervised(corpus, estimator=LaplaceProbDist)
            with open(settings.BASE_DIR+"/data/hmm.pkl", 'wb') as handle:
                pickle.dump(hmm, handle)
            return render(request, 'tagger/index.html', {'corpus': corpus})
        elif request.POST.get("index"):

            tags_file = open(settings.BASE_DIR+"/data/tags.json", 'rb')
            reader = codecs.getreader("utf-8")
            tags = json.load(reader(tags_file))
            true_index = len(corpus) - int(request.POST.get("index"))
            corpus_item = corpus[true_index]
            return render(request, 'tagger/corpus.html', {
                'tokens' : [t[0] for t in corpus_item],
                'corpus_item': corpus_item,
                'true_index': true_index,
                'tags': sorted(tags.items(), key=operator.itemgetter(1))})
    else:
        return render(request, 'tagger/corpus.html', {'corpus': corpus})

def index(request):
    if request.method == "POST":
        if request.POST.get("tokens"):
            with open(settings.BASE_DIR+"/data/corpus.pkl", 'rb') as handle:
                corpus = pickle.load(handle)

            tokens = ast.literal_eval(request.POST.get("tokens"))
            tagged = []
            i = 1
            for item in tokens:
                tagged.append((item,request.POST.get("token_"+str(i))))
                i += 1
            if tagged not in corpus:
                corpus.append(tagged)
                with open(settings.BASE_DIR+"/data/corpus.pkl", 'wb') as handle:
                    pickle.dump(corpus, handle)
                tag_set = unique_list(tag for sent in corpus for (word,tag) in sent)
                symbols = unique_list(word for sent in corpus for (word,tag) in sent)
                trainer = HiddenMarkovModelTrainer(tag_set, symbols)
                hmm = trainer.train_supervised(corpus, estimator=LaplaceProbDist)
                with open(settings.BASE_DIR+"/data/hmm.pkl", 'wb') as handle:
                    pickle.dump(hmm, handle)

            return render(request, 'tagger/index.html', {'corpus': corpus})

        else:
            if request.POST.get("random") == 'true':
                address = get_random_address()
            else:
                address = request.POST.get("address")

            tokens = regexp_tokenize(address, pattern=r'\d+|[^\r\n\t\f 0-9,]+|,', )

            if tokens:
                pkl_file = open(settings.BASE_DIR+"/data/hmm.pkl", 'rb')
                hmm = pickle.load(pkl_file)
                pkl_file.close()


                tagged = hmm.tag(tokens)

                tags_file = open(settings.BASE_DIR+"/data/tags.json", 'rb')

                reader = codecs.getreader("utf-8")
                tags = json.load(reader(tags_file))

                return render(request, 'tagger/index.html', {'address': address,
                                                              'tokens': tokens,
                                                              'tagged': tagged,
                                                              'tags': sorted(tags.items(), key=operator.itemgetter(1)) })

    return render(request, 'tagger/index.html', {})


