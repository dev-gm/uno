#!/usr/bin/env python

from enum import Enum
from random import randrange, shuffle
import sys


class Game:
    def __init__(self, usernames: tuple = ("Player 1"), hand_length: int = 5):
        self.deck = Deck(self.calculate_deck())
        self.discard = Discard(self.deck)
        self.discard.append(self.deck.draw())
        self.top_card = self.discard.get_top()
        self.players = list()
        for username in usernames:
            self.players.append(Player(username, self, hand_length))
        self.queue = list(self.players)
        self.currently_playing = self.queue.pop(0)
        self.over = False

    def start(self):
        while not self.over:
            top_card = self.discard.get_top().to_string()
            hand = self.currently_playing.to_string()
            print(f"Playing as {self.currently_playing.username}: ")
            print(f"{top_card}")
            print(hand)
            while not self.currently_playing.possible_moves:
                print("You are forced to draw a card\n")
                self.currently_playing.append(self.deck.draw())
                hand = self.currently_playing.to_string()
                print(hand)
            card_valid = False
            while not card_valid:
                card_index: int = int(input("Please enter the number of the card you wish to play (has to be possible): "))
                if card_index >= len(self.currently_playing):
                    continue
                if self.currently_playing[card_index] in self.currently_playing.possible_moves:
                    card_valid = True
            card = self.currently_playing[card_index]
            self.currently_playing.play(card_index)
            skip = False
            if card.symbol is CardSymbol.SKIP:
                skip = True
            elif card.symbol is CardSymbol.REVERSE:
                self.queue.reverse()
            elif card.symbol is CardSymbol.DRAW_TWO:
                next_player = self.queue[0]
                next_player.draw_two()
            elif card.symbol is CardSymbol.DRAW_FOUR:
                next_player = self.queue[0]
                next_player.draw_four()
            if card.color is CardColor.WILD:
                color: int = int(input("Please enter the color you wish to switch to ((1-4), [Blue, Green, Red, Yellow]): "))
                self.discard.edit_top(13, color)
            self.next_turn(skip)

    def next_turn(self, skip: bool):
        self.queue.append(self.currently_playing)
        self.currently_playing = self.queue.pop(0)
        if skip:
            self.currently_playing = self.queue.pop(0)

    def calculate_deck(self):
        output = list()
        for color in range(1, 5):
            output.append(Card(0, color))
        for symbol in range(1, 13):
            for color in range(1, 5):
                output.append(Card(symbol, color))
                output.append(Card(symbol, color))
        for i in range(4):
            output.append(Card(13, 0))
            output.append(Card(14, 0))
        return output


class Player(list):
    def __init__(self, username: str, game: Game, length: int):
        self.username = username
        self.game = game
        self.possible_moves = list()
        super().__init__()
        for i in range(length):
            card = self.game.deck.draw()
            self.append(card)
            if self.check_possible_move(card):
                self.possible_moves.append(card)

    def play(self, index):
        if self[index] not in self.possible_moves:
            return False
        card = self.pop(index)
        self.game.discard.discard(card)
        return True

    def draw_two(self):
        for i in range(2):
            self.append(self.game.deck.draw())

    def draw_four(self):
        for i in range(4):
            self.append(self.game.deck.draw())

    def check_possible_move(self, card):
        top_card = self.game.top_card
        top_color = top_card.color
        top_symbol = top_card.symbol
        color = card.color
        symbol = card.symbol
        if color == top_color:
            return True
        elif symbol == top_symbol:
            return True
        elif color is CardColor.WILD:
            return True
        elif symbol is CardSymbol.WILD:
            return True
        elif symbol is CardSymbol.DRAW_FOUR:
            return True
        else:
            return False


    def check_possible_moves(self):
        self.possible_moves = list()
        for card in self:
            if self.check_possible_move(card):
                self.possible_moves.append(card)
        return self.possible_moves

    def to_string(self):
        self.check_possible_moves()
        output = ""
        index = 0
        for card in self:
            output += f"{index}. {card.to_string()}"
            if card in self.possible_moves:
                output += f": possible\n"
            else:
                output += f": not possible\n"
            index += 1
        return output


class Deck(list):
    def __init__(self, default: list):
        self.default = default
        super().__init__()
        self = self.default
        shuffle(self)

    def add_many(self, many):
        for one in many:
            self.append(one)

    def to_list(self):
        return list(self)

    def list_to_deck(self, li):
        for item in li:
            self.append(item)

    def draw(self):
        if len(self) == 0:
            return None
        return self.pop(-1)


class Discard(list):
    def __init__(self, deck: Deck):
        self.deck = deck
        super().__init__()
        self.shuffle()

    def get_top(self):
        return self[-1]

    def edit_top(self, symbol: int, color: int):
        del self[-1]
        self.append(Card(symbol, color))

    def discard(self, card):
        if len(self.deck) == 0:
            self.shuffle()
        self.append(card)

    def reset(self):
        before = self
        self.clear()
        return before

    def shuffle(self):
        self.deck.list_to_deck(self.deck.default)
        shuffle(self.deck)
        self.append(self.deck.draw())
        return self.deck


class Card(object):
    def __init__(self, symbol: int, color: int):
        self.color = CardColor(color)
        self.symbol = CardSymbol(symbol)

    def to_string(self):
        return f"{self.color} {self.symbol}"


class CardColor(Enum):
    WILD = 0
    BLUE = 1
    GREEN = 2
    RED = 3
    YELLOW = 4


class CardSymbol(Enum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR  = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    SKIP = 10
    REVERSE = 11
    DRAW_TWO = 12
    WILD = 13
    DRAW_FOUR = 14


if __name__ == "__main__":
    players = ['Player 1', 'Player 2']
    for player in sys.argv[1:]:
        players[sys.argv[1:].index(player)] = player
    game = Game(tuple(players))
    game.start()
