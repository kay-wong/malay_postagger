#!/usr/bin/env python3

import re
import pickle
f = open('../data/malay_pos_tagged.txt').read()

#32 tags from Indonesian taglist for PanLocalisation Project
tagset = ['"', '(', ')', ',', '--', '.', ':', 'CC', 'CD', 'CDC', 'CDI', 'CDO', 'CDP', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NEG', 'NN', 'NNC', 'NNP', 'NNG', 'NNPS', 'NNS', 'PDT', 'POS', 'PRL', 'PRN', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SC', 'SYM', 'TO', 'UH',  'VB', 'VBD', 'VBG', 'VBI', 'VBN', 'VBP', 'VBT', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB']

def genTrainsetBasic(f, tagset):
    sents = f.strip().split('\n')
    sent_train = []
    for sent in sents:
        sentTokens=  []
        i=0
        for token in sent.split():
            split = token.split('/')
            if len(split)>1:
                token = split[0]
                tag = split[1].upper()
                if tag in tagset:
                    sentTokens.append((token, tag))                        
        sent_train.append(sentTokens)
    
    return sent_train

def genTrainset_reduced(f, tagset):
    sents = f.strip().split('\n')
    sent_train = []
    for sent in sents:
        sentTokens=  []
        i=0
        for token in sent.split():
            split = token.split('/')
            if len(split)>1:
                token = split[0]
                tag = split[1].upper()
                if tag in tagset:
                    if tag[:2] == 'VB':
                      sentTokens.append((token, 'VB'))
                    elif tag[:2] == 'CD':
                      sentTokens.append((token, 'CD'))
                    elif isnumber(token): #Misclassified numbers
                        sentTokens.append((token, 'CD'))    
                    elif tag[:2]=='NN':
                         if i>0 and tag=='NN' and token[0].upper()==token[0]: #not first word in sent
                             sentTokens.append((token, 'NNP'))
                         elif tag in ['NN', 'NNP', 'NNG']:
                             sentTokens.append((token, tag))                                
                         else:
                             sentTokens.append((token, 'NN'))
                    else:
                      sentTokens.append((token, tag))
            i+=1        
        sent_train.append(sentTokens)
    
    return sent_train

def fixTrainset(trainSet):
    sents_fixed = [[fixVerb(pos_pair[0], pos_pair[1]) if pos_pair[1]=='NN' else (pos_pair[0], pos_pair[1]) for pos_pair in sent] for sent in trainSet]
    sents_fixed = [[fixSymbol(pos_pair[0], pos_pair[1]) if re.match(r'[^\w]', pos_pair[0]) else (pos_pair[0], pos_pair[1]) for pos_pair in sent] for sent in sents_fixed]
    sents_fixed = [[(pos_pair[0], 'CD') if isNumber(pos_pair[0]) else (pos_pair[0], pos_pair[1]) for pos_pair in sent] for sent in sents_fixed]
    
    return sents_fixed

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def fixSymbol(token, tag):
    #Fix misclassified symbols
    if tag not in [',', '.', ':', '--']:
        if token in ['?', '.', '!']: #sentence terminators
            return (token, '.')
        elif token in ['"', '(', ')']:
            return (token, token)
        else:
            return (token, 'SYM')
    else: 
        return (token, tag)
    
def fixVerb(token, tag):
    verb_patterns=  [
    r'me(ny|ng|r|l|w|y|p|t|k|s)[a-z]*',
    r'mem(b|f|p|v)[a-z]*(kan|i)?',
    r'men(d|c|j|sy|z|t|s)[a-z]*(kan|i)?',
    r'meng(g|gh|kh|h|k|a|e|i|o|u)[a-z]*',
    r'menge[a-z]*(an)?',
    r'(mem|di)per[a-z]*(kan)?',
    r'ber[a-z]*(kan|an)?',
    r'te[^r][a-z]*',
    r'ke[a-z]*(an)?',
    r'di(per)?[a-z]*(kan|i)?'
    ]
    
    for pattern in verb_patterns:
        match = re.match(pattern, token)    
        if match:
            return (token, 'VB')
    
    return (token, tag)

def genTagset(trainSet):
    tagset = set([trainSet[i][j][1] for i in range(len(trainSet)) for j in range(len(trainSet[i]))])
    return tagset



'''
#===============================
#  Read Wordnet data
#===============================
#Read wordnet
#wn_msa = open('../data/wn-msa-all.tab').read()
msa = pd.read_csv('../data/wn-msa-all.tab', sep='\t', lineterminator='\n', header=None, names=['synset', 'lang', 'quality', 'word'])
good_tags = ['Y', 'O', 'M']
good_msa = msa[msa['quality'].isin(good_tags)]
posDic = {'a':'JJ', 'n': 'NN', 'v': 'VB', 'r': 'RB'}
good_msa['pos'] = good_msa['synset'].apply(lambda txt: posDic[txt[-1]])
'''


