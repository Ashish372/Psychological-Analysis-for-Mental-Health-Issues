from summarizer import PreprocessDocs
import re
import gensim
#text rank extractive summary
from gensim.summarization.summarizer import summarize
from WC import wordcloud_custom
# from senti import
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

# text = """One year ago I was not in a good place in my life. Everything around me was so negative and my thoughts were negative all day and night. I was always feeling bad . One day I remembered about The Secret and I started watching videos of the law of attraction. Later on I bought 2 books written by Rhonda. First book was The Magic and then later on I bought The Power.
# So I started reading The Magic and practiced it. I started doing all the things the book said. I started being happy and grateful for everything in my life and my life started to get amazing! Now everything is going just as I wanted. I have a perfect life now. I live in Germany with my family just like I had imagined. We are more wealthy and more happy and we can buy and get whatever our heart desires. These books really did change my life and I am so thankful.
# One bit of advice from me. Never give up on things you want. Be grateful for all the small and big things that you have."""
#Sentiment Analysis Block
def analyse (text):
    nlp = spacy.load('en_core_web_lg')
    nlp.add_pipe('spacytextblob')
    doc = nlp(text)
    # print (text)
    print(doc._.polarity)  # Polarity: -0.125

    if doc._.polarity >= 0.15:
        print("Patient's mental health is fine")
    elif doc._.polarity <= -0.2:
        print("The patient will have to visit in person and get treated")
    else:
        print("Patient needs treatment ")

    # WordCloud Block
    cloud = wordcloud_custom(text)

    # Summary Block
    preprocess = PreprocessDocs
    text1 = preprocess.read_article(text)
    result = summarize(".\n".join(text1))
    s = re.sub('\.+', '.', result)
    print("_______________________________________________________________")
    print(s)
    print("___________________________________________________________________")