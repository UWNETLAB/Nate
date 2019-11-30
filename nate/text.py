"""
This class accepts text data and outputs co-occurrence networks
"""

from nate.helpers import window_text, search_entities
import spacy
nlp = spacy.load('en')
import re
