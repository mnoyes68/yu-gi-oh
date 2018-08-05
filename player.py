class Player():
    def __init__(self, name, deck):
        self.name = name
        self.deck = deck
        self.hand = []
        self.life_points = 2000

    def draw_card(self):
        c = self.deck.cards.pop(0)
        self.hand.append(c)
        print self.name + " drew " + c.name

class ComputerPlayer(Player):
    player_type = "Computer"

    def __init__(self, name, deck):
        Player.__init__(self, name, deck)

