import cards

class Player():
    def __init__(self, name, deck):
        self.name = name
        self.deck = deck
        self.hand = cards.Hand()
        self.board = Board()
        self.life_points = 2000

    def draw_card(self):
        c = self.deck.cards.pop(0)
        self.hand.cards.append(c)
        print self.name + " drew " + c.name

class Board():
    def __init__(self):
        self.monster_spaces = []
        self.magic_trap_spaces = []
        for i in range(0,5):
            self.monster_spaces.append(Space("Monster"))
            self.magic_trap_spaces.append(Space("Magic-Trap"))

class Space():
    def __init__(self, card_type):
        self.card_type = card_type
        self.occupied = False
        self.card = None

    def add_card(self, card):
        self.card = card
        self.occupied = True

    def remove_card(self, card):
        self.card = None
        self.occupied = False

class ComputerPlayer(Player):
    player_type = "Computer"

    def __init__(self, name, deck):
        Player.__init__(self, name, deck)

