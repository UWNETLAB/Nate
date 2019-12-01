def window_text(string_of_text, window_lr=3):
    """
    This function splits a string into tokens on each space. Then it iterates
    over each token and takes add n words to a new list where n = the number of
    ``window_lr`` * 2 + 1. This is because ``window_lr'' is the number of
    words to grab to the left AND to the right of each token in the string.
    If ``window_lr'' = 2, then it will take the token itself, 2 words to the
    left of the token, and 2 words to the right of a token. The result is a
    window of 5 words. As a result of this design decision, the smallest window
    possible is 3 words, which can be given by ``window_lr'' = 1. Finally, the
    windows at the start and end of a text string will be smaller than the rest
    because they will have fewer words at the start (nothing / less to the left)
    and at the end (nothing / less to the right). This function is designed to
    take in a string. If the string is pre-processed (which is should be), make
    sure it is receiving a string, not tokenized from another package, like
    spacy or nltk.

    The output of this function is a new list of windowed strings. It can be
    fed into functions like construct_conet() to construct a co-occurrence
    network where co-occurrence happens between words within a moving window.
    Obviouslly, this is the function that makes the windows, not the
    co-occurrence network.
    """
    tokens = string_of_text.split()
    for each in tokens:
        context = []
        for index in range(len(tokens)):
            start = max(0, index-window_lr)
            finish = min(len(tokens), index+window_lr)
            left = " ".join(tokens[start:index])
            right = " ".join(tokens[index+1:finish])
            context.append("{} {} {}".format(left, tokens[index], right))
    return context


def search_entities(raw_text_string, search):
    """
    Helper function for construct_entity_conet(). Iterates over a list
    of entities and looks to see if they are present in a given text
    string. If they are, then it will append the entity to a list for
    each text. These lists of ents appearing in texts can be used to
    construct a network of entities that co-occurr within texts.
    """
    ents = []
    for entity in search:
        if entity.lower() in raw_text_string.lower():
            ents.append(entity.lower())
    return ents


def adjmat_to_wel(adjmat, remove_self_loops=True):
    """
    Accepts an adjacency matrix and outputs a weighted edgelist.
    """
    adjmat = pd.read_csv('~/Desktop/testing/ajm.csv', index_col = 0)
    adjmat.fillna(0, inplace=True)

    if remove_self_loops is True:
        # zero out the diagonal
        for i in adjmat.index:
            adjmat.loc[i,i] = 0
    else:
        pass

    wel=[('i','j','Weight')]
    for source in adjmat.index.values:
        for target in adjmat.index.values:
            if adjmat[source][target] > 0:
                wel.append((target,source,adjmat[source][target]))
    return wel
