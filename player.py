import cards

class Player():
    def __init__(self, name, deck):
        self.name = name
        self.deck = deck
        self.hand = cards.Hand()
        self.board = Board()
        self.life_points = 4000

    def draw_card(self):
        c = self.deck.cards.pop(0)
        self.hand.cards.append(c)
        print self.name + " drew " + c.name

    def increase_life_points(self, amount):
        self.life_points += amount

    def decrease_life_points(self, amount):
        self.life_points -= amount
        if self.life_points <= 0:
            self.life_points = 0
            print "GAME OVER!"
        print self.name + "'s life points are now " + str(self.life_points)

class Board():
    def __init__(self):
        self.monster_spaces = []
        self.magic_trap_spaces = []
        for i in range(0,5):
            self.monster_spaces.append(Space("Monster"))
            self.magic_trap_spaces.append(Space("Magic-Trap"))

    def get_occupied_monster_spaces(self):
        occupied_spaces = [s for s in self.monster_spaces if s.occupied == True]
        return len(occupied_spaces)

    def get_monsters(self):
        return [s.card for s in self.monster_spaces if s.occupied == True]

    def destroy_monster(self, monster):
        for space in self.monster_spaces:
            if monster == space.card:
                space.remove_card()
                print monster.name + " is now destroyed"
                break

class Space():
    def __init__(self, card_type):
        self.card_type = card_type
        self.occupied = False
        self.card = None

    def add_card(self, card):
        self.card = card
        self.occupied = True

    def remove_card(self):
        self.card = None
        self.occupied = False

class ComputerPlayer(Player):
    player_type = "Computer"

    def __init__(self, name, deck):
        Player.__init__(self, name, deck)

