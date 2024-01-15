from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image
from os import path, getcwd
import numpy as np

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class wordcloud_custom:
    def __init__(self,text):
        # removed punctuation and stop words
        filteredlst = self.punctuation_stop(text)

        # list of unwanted words
        unwanted = ['one', 'guy', 'really', 'mean', 'little bit', 'thing', 'say', 'go', 'actually',
                    'even', 'probably', 'going', 'said', 'something', 'okay', 'maybe', 'got', 'well', 'way']

        # remove unwanted words
        text = " ".join([ele for ele in filteredlst if ele not in unwanted])

        # get the working directory
        d = getcwd()

        # numpy image file of mask image
        mask_logo = np.array(Image.open(path.join(d, "Bigger_Pockets_Logo4.png")))

        # create the word cloud object
        wc = WordCloud(background_color="white", max_words=2000, max_font_size=90, random_state=1, mask=mask_logo,
                       stopwords=STOPWORDS)
        wc.generate(text)

        image_colors = ImageColorGenerator(mask_logo)

        plt.figure(figsize=[10, 10])
        plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
        plt.axis('off')
        # plt.show()
        #Save wordcloud
        plt.savefig("static/WCresult2.png")
        plt.close()

    def punctuation_stop(self, text):
        """remove punctuation and stop words"""
        filtered = []
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text)
        for w in word_tokens:
            if w not in stop_words and w.isalpha():
                filtered.append(w.lower())

        return filtered