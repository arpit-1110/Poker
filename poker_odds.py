import numpy as np
import itertools
import argparse

cards = ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']
suits = ['S', 'H', 'C', 'D']

class Card:
    def __init__(self, val, suit):
        self.val = val
        self.suit = suit

    def __str__(self):
        return f'{self.val} {self.suit}'

class Hand:
    def __init__(self, card1, card2):
        self.card1 = card1
        self.card2 = card2
        self.hand_counts = {
        9 : [0, 'Straight Flush'],
        8 : [0, 'Four of a Kind'],
        7 : [0, 'Full House'],
        6 : [0, 'Flush'],
        5 : [0, 'Straight'],
        4 : [0, 'Three of a Kind'],
        3 : [0, 'Two Pair'],
        2 : [0, 'Pair'],
        1 : [0, 'High Card'],
        }

    def count(self, n):
        self.hand_counts[n][0] += 1

    def __str__(self):
        res = f'{self.card1} {self.card2} makes:\n'
        pct = np.asarray([_[0] for _ in self.hand_counts.values()])
        pct = pct/pct.sum()*100
        for i, hand in enumerate(self.hand_counts.values()):
            res += f'{hand[1]}: {round(pct[i], 4)}%\n'
        return res

value = {c:13-i for i, c in enumerate(cards)}

def high_card(cards):
    return max([value[c.val] for c in cards])

def same_suit(cards):
    return len(set([c.suit for c in cards])) == 1

def is_straight(cards):
    sc = sorted(cards, key=lambda x: value[x.val])
    prev = value[sc[0].val]
    if value[sc[1].val] == 1 and prev == 13:
        prev = 0
    for j in range(1, len(cards)):
        curr = value[sc[j].val]
        if curr != prev+1:
            return False
        prev = curr
    return True

def is_4_of_a_kind(cards):
    _, counts = get_same_cards(cards)
    if len(counts) == 2 and counts.max() == 4:
        return True
    return False

def is_full_house(cards):
    _, counts = get_same_cards(cards)
    if len(counts) == 2 and counts.max() == 3:
        return True
    return False

def is_trio(cards):
    _, counts = get_same_cards(cards)
    if len(counts) == 3 and counts.max() == 3:
        return True
    return False

def is_2_pair(cards):
    _, counts = get_same_cards(cards)
    if len(counts) == 3 and counts.max() == 2:
        return True
    return False

def is_pair(cards):
    _, counts = get_same_cards(cards)
    if len(counts) == 4:
        return True
    return False

def get_same_cards(cards):
    vals = np.asarray([value[c.val] for c in cards])
    return np.unique(vals, return_counts=True)

def get_val(vals, counts, c):
    return sorted(vals[counts == c], key=lambda x:-x)

def hand(cards):
    hc = high_card(cards)
    vals, counts = get_same_cards(cards)
    if same_suit(cards) and is_straight(cards):
        return (9, [hc])
    elif is_4_of_a_kind(cards):
        f = get_val(vals, counts, 4)
        return (8, f)
    elif is_full_house(cards):
        f1 = get_val(vals, counts, 3)
        f2 = get_val(vals, counts, 2)
        return (7, f1 + f2)
    elif same_suit(cards):
        return (6, [hc])
    elif is_straight(cards):
        return (5, [hc])
    elif is_trio(cards):
        f1 = get_val(vals, counts, 3)
        f2 = get_val(vals, counts, 1)
        return (4, f1 + f2)
    elif is_2_pair(cards):
        f1 = get_val(vals, counts, 2)
        f2 = get_val(vals, counts, 1)
        return (3, f1 + f2)
    elif is_pair(cards):
        f1 = get_val(vals, counts, 2)
        f2 = get_val(vals, counts, 1)
        return (2, f1 + f2)
    else:
        return (1, get_val(vals, counts, 1))

def get_best_hand(all_cards):
    all_hands = []
    for cards in itertools.combinations(all_cards, 5):
        all_hands.append(hand(cards))

    return max(all_hands)

def draw_cards(Deck, n):
    cards = []
    for _ in range(n):
        cards.append(Deck.pop(0))
    return cards

def comp_two_hands(hand1, hand2, Deck):
    table = draw_cards(Deck, 5)
    bh1 = get_best_hand(hand1+table)
    bh2 = get_best_hand(hand2+table)
    if bh1 > bh2:
        return -1, bh1, bh2
    elif bh1 < bh2:
        return 1, bh1, bh2
    else:
        return 0, bh1, bh2

parser = argparse.ArgumentParser()
parser.add_argument('--hand1', type=str, required=True)
parser.add_argument('--hand2', type=str)
parser.add_argument('--comp', action='store_true')
parser.add_argument('--overall_equity', action='store_true')

args = parser.parse_args()

def parse_hand(hand):
    return [_.split(' ') for _ in hand.split(' & ')]


def create_deck(remove_cards=[]):
    Deck = []
    for card in cards:
        for suit in suits:
            if (card, suit) in remove_cards:
                continue
            Deck.append(Card(card, suit))
    return Deck

if args.comp:
    hand1 = parse_hand(args.hand1)
    hand2 = parse_hand(args.hand2)
    Deck = create_deck(hand1+hand2)
    f = lambda x: Card(x[0], x[1])
    hand1 = [f(_) for _ in hand1]
    hand2 = [f(_) for _ in hand2]

    hand1_count = 0
    hand2_count = 0
    tie_count = 0
    nseeds = 10
    nsims = 200

    Hand1 = Hand(*hand1)
    Hand2 = Hand(*hand2)

    for seed in range(nseeds):
        np.random.seed(seed)
        for sim in range(nsims):
            deck_shuffled = np.random.permutation(Deck).tolist()
            res, h1, h2 = comp_two_hands(hand1, hand2, deck_shuffled.copy())
            Hand1.count(h1[0])
            Hand2.count(h2[0])
            if res == -1:
                hand1_count += 1
            elif res == 1:
                hand2_count += 1
            else:
                tie_count += 1

    h1_win = hand1_count/nseeds/nsims*100
    h2_win = hand2_count/nseeds/nsims*100
    tie = tie_count/nseeds/nsims*100

    print(f'Hand1: {hand1[0]}, {hand1[1]} wins {h1_win}%')
    print(f'Hand2: {hand2[0]}, {hand2[1]} wins {h2_win}%')
    print(f'Tie happens: {tie}%')
    print(Hand1)
    print(Hand2)
elif args.overall_equity:
    hand1 = parse_hand(args.hand1)
    Deck = create_deck(hand1)
    f = lambda x: Card(x[0], x[1])
    hand1 = [f(_) for _ in hand1]

    nseeds = 10
    nsims = 500
    hand1_count = 0
    hand2_count = 0
    tie_count = 0

    Hand1 = Hand(*hand1)
    for seed in range(nseeds):
        np.random.seed(seed)
        for i in range(nsims):
            rnd_card = np.random.randint(0, len(Deck))
            rnd_card2 = np.random.randint(0, len(Deck))
            while rnd_card2 == rnd_card:
                rnd_card2 = np.random.randint(0, len(Deck))
            hand2 = [Deck[rnd_card], Deck[rnd_card2]]
            Hand2 = Hand(*hand2)
            deck_shuffled = np.random.permutation(Deck).tolist()
            res, h1, h2 = comp_two_hands(hand1, hand2, deck_shuffled.copy())
            Hand1.count(h1[0])
            Hand2.count(h2[0])
            if res == -1:
                hand1_count += 1
            elif res == 1:
                hand2_count += 1
            else:
                tie_count += 1
    h1_win = hand1_count/nseeds/nsims*100
    h2_win = hand2_count/nseeds/nsims*100
    tie = tie_count/nseeds/nsims*100

    print(f'Hand1: {hand1[0]}, {hand1[1]} wins {h1_win}%')
    print(f'Hand2 wins {h2_win}%')
    print(f'Tie happens: {tie}%')
    print(Hand1)
    # print(Hand2)

else:
    hand1 = parse_hand(args.hand1)
    Deck = create_deck(hand1)
    f = lambda x: Card(x[0], x[1])
    hand1 = [f(_) for _ in hand1]

    nseeds = 10
    nsims = 500

    Hand1 = Hand(*hand1)

    for seed in range(nseeds):
        np.random.seed(seed)
        for sim in range(nsims):
            deck_shuffled = np.random.permutation(Deck).tolist()
            table = draw_cards(deck_shuffled, 5)
            h1 = get_best_hand(table+hand1)
            Hand1.count(h1[0])

    print(Hand1)
