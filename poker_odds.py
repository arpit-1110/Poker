import numpy as np
import itertools
import argparse

cards = ['A', 'K', 'Q', 'J', 10, 9, 8, 7, 6, 5, 4, 3, 2]
suits = ['S', 'H', 'C', 'D']

class Card:
    def __init__(self, val, suit):
        self.val = val
        self.suit = suit

    def __str__(self):
        return f'{self.val} {self.suit}'

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
    if get_best_hand(hand1+table) > get_best_hand(hand2+table):
        return -1
    elif get_best_hand(hand1+table) < get_best_hand(hand2+table):
        return 1
    else:
        return 0

Deck = []

hand1 = [('A', 'D'), ('A', 'H')]
hand2 = [('K', 'S'), ('Q', 'S')]

for card in cards:
    for suit in suits:
        if (card, suit) in hand1+hand2:
            continue
        Deck.append(Card(card, suit))

f = lambda x: Card(x[0], x[1])
hand1 = [f(_) for _ in hand1]
hand2 = [f(_) for _ in hand2]

hand1_count = 0
hand2_count = 0
tie_count = 0
nseeds = 10
nsims = 100

for seed in range(nseeds):
    for sim in range(nsims):
        deck_shuffled = np.random.permutation(Deck).tolist()
        if comp_two_hands(hand1, hand2, deck_shuffled.copy()) == -1:
            hand1_count += 1
        elif comp_two_hands(hand1, hand2, deck_shuffled.copy()) == 1:
            hand2_count += 1
        else:
            tie_count += 1

h1_win = hand1_count/nseeds/nsims*100
h2_win = hand2_count/nseeds/nsims*100
tie = tie_count/nseeds/nsims*100

print(f'Hand1: {hand1[0]}, {hand1[1]} wins {h1_win}%')
print(f'Hand2: {hand2[0]}, {hand2[1]} wins {h2_win}%')
print(f'Tie happens: {tie}%')
