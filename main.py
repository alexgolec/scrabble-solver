import board.board as board
import lists.lists as lists
import lists.pattern as pattern
import time

def words_for_pos(brd, pos, direction, wordlist, gutter):
    '''
    Given a board, a position, and a direction, get the words that would fit.
    '''
    print 'Searching board space'
    starttime = time.time()
    ret = []
    patterns = brd.make_patterns(pos, direction, len(gutter))
    for pat in patterns:
        p = pattern.Pattern(pat.get_pattern())
        matches = p.find_matches(wordlist, gutter)
        for m in matches:
            # check that the intersection words are valid
            tile = board.Word([board.BoardTile(pat[i].pos, m[i])
                               for i in xrange(0, len(pat))])
            ints = brd.get_intersecting_words(tile)
            if any(i not in wordlist for i in ints):
                continue
            # no need to use a full blown Word object, since we can trust the
            # returned list or correctly ordered
            ret.append(tile)
    endtime = time.time()
    print 'Filled %d patterns in %.2f seconds' % (len(patterns), float(endtime) -
                                                     starttime)
    return ret

import scoring

def get_best_words(b, gutter):
    ret = []
    for i in xrange(0, b.width):
        for j in xrange(0, b.height):
            pos = (i, j)
            if pos not in b.board:
                continue
            words = words_for_pos(b, pos, board.ACROSS, lists.get_wordlist(),
                                  gutter)
            ret.extend(words)
            words = words_for_pos(b, pos, board.DOWN, lists.get_wordlist(),
                                  gutter)
            ret.extend(words)
    return sorted(ret, key=lambda w: scoring.score_word(w))

if __name__ == '__main__':
    import random
    import string

    from ui import board_ui

    gutter = [random.choice(string.lowercase) for i in xrange(0, 7)]

    class BoardDelegate(board_ui.ScrabbleBoardDelegate):
        def __init__(self, wordlist, board_state):
            self.wordlist = wordlist
            self.board_state = board_state
            self.best_words = None
            self.hand = {}
        def getNextBestWord(self, sender):
            if self.best_words is None:
                self.best_words = get_best_words(
                    self.board_state, self.getHand())
            if self.best_words:
                #best = self.best_words.pop()
                best = self.best_words[-1]
                return [i for i in best if i.pos not in self.board_state.board]
            else:
                return None
        def boardWasModified(self, sender):
            self.best_words = None
        def tileWasCleared(self, sender, pos):
            try:
                self.board_state.manually_delete_tile(pos)
            except KeyError:
                pass
            if pos[1] == 15:
                del self.hand[pos[0]]
                print 'deleted hand pos', pos[0]
        def letterWasInput(self, sender, letter, pos):
            self.board_state.manually_put_tile(
                board.BoardTile(pos, letter)
            )
            if pos[1] == 15:
                self.hand[pos[0]] = letter
                print 'set hand position', pos[0], 'to', letter
                print self.getHand()
        def acceptWord(self, sender, word):
            if word:
                self.board_state.put_word(word)
        def getHand(self):
            return ''.join(self.hand[i] for i in self.hand)

    game = board_ui.ScrabbleBoard(
        delegate=BoardDelegate(lists.get_wordlist(), board.BoardState(15, 15))
    )
    game.start()
