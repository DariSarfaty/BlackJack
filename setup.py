import random

decks = 6


class Card:
    def __init__(self, suit, rank):
        self.rank = rank
        self.suit = suit
        self.face_down = False
        self.ace = rank == "A"
        self.value = 0
        self.update_value()

    def __str__(self):
        if self.face_down:
            return 'a facedown card'
        return f'{self.rank} of {self.suit}'

    def update_value(self):
        if self.face_down:
            val = 0
        elif self.rank in "KQJ":
            val = 10
        elif self.rank == "A":
            val = 11
        else:
            val = int(self.rank)
        self.value = val

    def up(self):
        self.face_down = False
        self.update_value()

    def down(self):
        self.face_down = True
        self.update_value()


class Hand:
    def __init__(self):
        self.cards = []
        self.aces = False
        self.value = 0
        self.blackjack = True

    def __str__(self):
        if len(self.cards) == 0:
            return 'an empty hand'
        s = f'{self.cards[0].__str__()}'
        for card in self.cards[1:]:
            s += " and "
            s += card.__str__()
        s += f', value {self.value}'
        if self.aces:
            s += f' or {self.value - 10}'
        return s

    def update_value(self):
        self.blackjack = False
        self.update_aces()
        val = sum(card.value for card in self.cards)
        if self.aces and val > 21:
            val = val - 10
        self.value = val
        if self.value == 21 and len(self.cards) == 2:
            self.blackjack = True

    def update_aces(self):
        self.aces = any(card.ace for card in self.cards)

    def draw(self, pile, down = False):
        card = pile.draw()
        if down:
            card.down()
        self.cards.append(card)
        self.update_value()

    def split(self):
        return self.cards.pop(0)

    def receive(self, card):
        self.cards.append(card)

    def reveal(self):
        for card in self.cards:
            card.up()
        self.update_value()

    def clear(self, pile):
        for i in range(len(self.cards)):
            pile.receive(self.cards.pop(0))
        self.update_value()

class Pile:
    def __init__(self):
        self.shoe = []
        self.trash = []

    def check(self):
        if len(self.shoe) <= 0.6 * decks * 52:
            print(f'{self}, shuffling')
            self.redraw()
            self.shuffle()

    def shuffle(self):
        random.shuffle(self.shoe)

    def redraw(self):
        for i in range(len(self.trash)):
            self.receive(self.trash.pop(0))

    def receive(self, card):
        card.up()
        self.shoe.append(card)

    def throw(self, card):
        self.trash.append(card)

    def draw(self):
        return self.shoe.pop(0)

    def __str__(self):
        return f'shoe contains {len(self.shoe)} cards and trash contains {len(self.trash)} cards'




class Table:
    def __init__(self):
        self.dealer = Hand()
        self.player = Hand()
        self.balance = 10000
        self.split_hand = Hand()
        self.deck = Pile()
        for i in range(decks):
            for suit in ["Spade", "Heart", "Diamond", "Club"]:
                for rank in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]:
                    self.deck.receive(Card(suit, rank))
        self.deck.shuffle()

    def deal(self):
        self.player.draw(self.deck)
        self.dealer.draw(self.deck, True)
        self.player.draw(self.deck)
        self.dealer.draw(self.deck)
        print(f'dealer: {self.dealer}\nplayer: {self.player}')

    def play(self):
        side = 0
        pay1, pay2 = 0, 0
        payout = 0
        self.deal()
        if self.player.blackjack:
            print("player blackjack")
            self.dealer.reveal()
            print(f'dealer: {self.dealer}')
            if self.dealer.blackjack:
                return 0
            else:
                return 1.5
        if self.dealer.value == 11:
            if input("insure? y/n ").lower() == "y":
                self.dealer.reveal()
                if self.dealer.blackjack:
                    print("dealer blackjack")
                    return 0
                else:
                    print("no dealer blackjack")
                    side = -0.5
        if self.player.cards[0].value == self.player.cards[1].value:
            if input("split? y/n ").lower() == "y":
                self.split_hand.receive(self.player.split())
                self.player.draw(self.deck)
                self.split_hand.draw(self.deck)
                print(self.player)
                pay1 = self.hit(self.player)
                print(self.split_hand)
                pay2 = self.hit(self.split_hand)
        else:
            pay1 = self.hit(self.player)


        self.dealer.reveal()
        while self.dealer.value <= 16:
            self.dealer.draw(self.deck)
        print(f'dealer: {self.dealer}')

        dealer = self.dealer.value
        hand = self.player.value
        split = self.split_hand.value
        if hand > 21:
            print("bust")
            payout = -1*pay1
        elif dealer > 21:
            payout = pay1
        elif hand > dealer:
            print("win")
            payout = pay1
        elif hand == dealer:
            print("push")
            payout = 0
        else:
            print("dealer won")
            payout = -1*pay1
        if pay2 != 0:
            if split > 21:
                print("bust")
                payout += -1*pay2
            elif dealer > 21:
                payout = pay2
            if split > dealer:
                print("win")
                payout += pay2
            elif split == dealer:
                print("push")
                payout += 0
            else:
                print("dealer won")
                payout += -1 * pay2

        self.clear()

        return payout + side

    def hit(self, hand):
        if input("double? y/n ").lower() == "y":
            self.player.draw(self.deck)
            print(hand)
            return 2
        inp = input("hit? y/n ").lower()
        while hand.value < 21 and inp == "y":
            hand.draw(self.deck)
            print(hand)
            inp = input("hit? y/n ").lower()
        return 1
    def clear(self):
        self.dealer.clear(self.deck)
        self.player.clear(self.deck)
        self.split_hand.clear(self.deck)
        self.deck.check()

game = Table()
while input("play again? y/n ").lower() == "y":
    bet = int(input("bet: "))
    game.balance += bet * game.play()
    print(f'current balance: {game.balance}')
