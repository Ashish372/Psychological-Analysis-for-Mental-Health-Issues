import re
import spacy
NLP = spacy.load('en_core_web_lg')
#max number of word line 63 if file tooo lagre will give error.bascially no of word that i can use in nlp
NLP.max_length = 3500000


class PreprocessDocs:
    """ cleaning documents before passing them to summarizer for a clean summary """
    @staticmethod
    def read_article(text):
        """ reading file data and cleaning it """
        # Remove all non Ascii Chars
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        # Remove every special char except the words and numbers
        text = re.sub(r'([^/A-Za-z0-9\.\'?-])', ' ', text)
        # Remove super big encoded words (Regex not working)
        text = ' '.join([w for w in text.split() if len(w) < 15])
        rn_pattern = re.compile(r'\s[rn]\s')
        found_rn_pattern = rn_pattern.findall(text)
        filedata = text
        filedata = re.sub(' +', ' ', filedata)
        filedata = NLP(filedata)

        # Merge two wrongly splitted sentences
        filedata = [str(x) for x in filedata.sents]
        filedata = [x[:].replace('\n', ' ') for x in filedata]
        filedata = ('\n'.join(filedata))

        # Data Cleaning to remove sentences that are not important
        filedata = re.sub(' +', ' ', filedata)

        "add your custom stop words"
        custom_stop_words = []

        def clean_helper(filedata):
            for word in filedata.split(' '):
                if word in custom_stop_words:
                    return False

            filedata = re.sub(r"[\d-]", '', filedata)
            filedata = re.sub(r"[^a-zA-Z0-9 ]", '', filedata)
            # Remove words with length smaller than three
            filedata = re.sub(r'\b\w{1,2}\b', ' ', filedata)
            filedata = re.sub(r'\s+', ' ', filedata).strip()
            filedata = filedata.split()
            # "Remove duplicate words in string"
            filedata = " ".join(sorted(set(filedata), key=filedata.index))

            if len(filedata.split(' ')) > 4:
                return True
            return False

        filedata = list(filter(clean_helper, filedata.splitlines()))
        filedata = '\n'.join(filedata)

        # Used Spacy to split the sentences
        def spacy_clean_helper(filedata):
            filedata = str(filedata)
            filedata = NLP(re.sub(r' +', ' ', filedata))
            #remove pun stopword space e.t.c
            filedata = NLP(" ".join([str(x.lemma_) for x in filedata if not x.is_stop and x.pos_ !=
                                     'PUNCT' and x.pos_ != 'NUM' and\
                                         x.pos_ != 'SPACE']).lower())

            filedata = str(filedata)
            # Remove sentences with less than 2 words or sentences with more
            # than 25 words
            if len(filedata.split(' ')) > 2 and len(filedata.split(' ')) < 20:
                return True
            return False

        sentences = list(filter(spacy_clean_helper, filedata.splitlines()))
        sentences = [str(sentence) for sentence in sentences]

        return sentences

# text = """ The golden rule for selecting characters in story writing is “Fewer is better”. Story writing would more effectively convey its meaning if it has very few characters – one protagonist, one other main character, and no supporting or side characters would be ideal.
#
# The animating character with perfect adjectives and examples is a must however, typically while writing short stories, do not fall overdo the characterization.
#
# Time frame and place constitute the setting of story writing. The setting is often decorated with descriptions of scenes such as supermarket, bedroom, crowded metro train, or drizzling evening… again unlimited list. These descriptions are very important to make the reader immerse in the plot.
#
# Unit of time frame may vary from hours to days to weeks to years. The golden rule in selecting time frame for story writing is “keep it shorter” and “have it single”. Story writing that has setting of few hours may typically be clearer and more effective than with setting of few months or years.
#
# vividly describe surroundings. must be absolutely clear and very importantly be appealing to five senses of your readers. Be poetic, use suitable adjectives, script dialogues, or even deploy side characters… do whatever you need to ensure that the reader lives your story while reading.
#
# The plot is the flesh and muscles of story writing. It comprises events and characters’ actions. The more creatively you describe and logically connect the events and actions, the stronger the plot would be, and the stronger the plot you create, the better interest would it generate among readers. A plot has a start, body, and end that are linked sequentially by events and character actions. """
# preprocess = PreprocessDocs
# text = preprocess.read_article(text)
# result = summarize(".\n".join(text))
# s = re.sub('\.+', '.', result)
# print(s)