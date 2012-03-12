'''
Classes for reading and managing wordlists.
'''

###############################################################################
# Singleton management

__wordlists = {}

def get_wordlist(name='ntlworld.wordlist.txt'):
    if name not in __wordlists:
        __wordlists[name] = WordList(name)
    return __wordlists[name]

###############################################################################

import os

def make_writeback_func(wordlist, path):
    def func():
        'write this wordlist out to the relevant file, if necessary'
        # otherwise go ahead and write back
        tmp_file = path+'.tmp'
        with open(tmp_file, 'w') as f:
            for word in sorted(wordlist.wordlist):
                # this if is not strictly necessary, but it makes it easier to
                # recover from minor bugs in the reading and writing code
                if word:
                    f.write(word+'\n')
        os.rename(tmp_file, path)
    return func

import atexit

class WordList:
    '''
    Represents a wordlist, and supports various query types.
    '''
    def __init__(self, name):
        # apparently __file__ is not defined when the module is called from the
        # command line. detect this situation and complain if necessary.
        try:
            cur_file = __file__
            del cur_file
        except NameError:
            raise ValueError('__file__ is not defined. Don\'t run this as a \
                    standalone module.')

        # until this object is modified, we don't need to write it out to disk
        self.__did_register_writeback = False

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(cur_dir, 'data', name)

        with open(self.path, 'r') as f:
            self.wordlist = set()
            # yes, this could be more pythonic, but it avoids creating an
            # unnecessary list object. or maybe the compiler optimizes that
            # out?
            for line in f.xreadlines():
                self.wordlist.add(line.replace('\n', ''))
    def contains(self, word):
        'Checks to see if the wordlist recognizes this word.'
        return word.lower() in self.wordlist
    def add_word(self, word):
        'Manually adds a word to the wordlist.'
        self.wordlist.add(word.lower())
        self.__register_writeback()
    def remove_word(self, word):
        'Manually removes a word from the wordlist.'
        self.wordlist.remove(word.lower())
        self.__register_writeback()
    def __register_writeback(self):
        'Register that the wordlist needs to be written back to disk.'
        if self.__did_register_writeback:
            return
        else:
            atexit.register(make_writeback_func(self, self.func))
            self.__did_register_writeback = True
