import re
import spacy
NLP = spacy.load('en_core_web_lg')
#max number of word line 63 if file too lagre will give error.bascially no of word that i can use in nlp
NLP.max_length = 3500000


class PreprocessDocs:
    """ cleaning documents before passing them to summarizer for a clean summary """
    @staticmethod
    def read_text(text):
        """ reading file data and cleaning it """
        # Remove all non Ascii Chars
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        # Remove every special char except the words and numbers
        text = re.sub(r'([^/A-Za-z0-9\.\'?-])', ' ', text)
        # Remove super big encoded words (Regex not working)
        text = ' '.join([w for w in text.split() if len(w) < 15])
        rn_pattern = re.compile(r'\s[rn]\s')
        found_rn_pattern = rn_pattern.findall(text)
        filetext = text
        filetext = re.sub(' +', ' ', filetext)
        filetext = NLP(filetext)

        # Merge two wrongly splitted sentences
        filetext = [str(x) for x in filetext.sents]
        filetext = [x[:].replace('\n', ' ') for x in filetext]
        filetext = ('\n'.join(filetext))

        # Data Cleaning to remove sentences that are not important
        filetext = re.sub(' +', ' ', filetext)

        "add your custom stop words"
        custom_stop_words = []

        def clean_stage1(filetext):
            for word in filetext.split(' '):
                if word in custom_stop_words:
                    return False

            filetext = re.sub(r"[\d-]", '', filetext)
            filetext = re.sub(r"[^a-zA-Z0-9 ]", '', filetext)
            # Remove words with length smaller than three
            filetext = re.sub(r'\b\w{1,2}\b', ' ', filetext)
            filetext = re.sub(r'\s+', ' ', filetext).strip()
            filetext = filetext.split()
            # "Remove duplicate words in string"
            filetext = " ".join(sorted(set(filetext), key=filetext.index))

            if len(filetext.split(' ')) > 4:
                return True
            return False

        filetext = list(filter(clean_stage1, filetext.splitlines()))
        filetext = '\n'.join(filetext)

        # Used Spacy to split the sentences
        def clean_stage2(filetext):
            filetext = str(filetext)
            filetext = NLP(re.sub(r' +', ' ', filetext))
            #remove pun stopword space e.t.c
            filetext = NLP(" ".join([str(x.lemma_) for x in filetext if not x.is_stop and x.pos_ !=
                                     'PUNCT' and x.pos_ != 'NUM' and\
                                         x.pos_ != 'SPACE']).lower())

            filetext = str(filetext)
            # Remove sentences with less than 2 words or sentences with more
            # than 25 words
            if len(filetext.split(' ')) > 2 and len(filetext.split(' ')) < 20:
                return True
            return False

        sentences = list(filter(clean_stage2, filetext.splitlines()))
        sentences = [str(sentence) for sentence in sentences]

        return sentences