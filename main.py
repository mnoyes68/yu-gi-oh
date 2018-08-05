import cards
import player
import game 
import random

# Create Cards
sdy_001 = cards.MonsterCard("Mystical Elf", "SDY-001", 800, 2000)
sdy_002 = cards.MonsterCard("Feral Imp", "SDY-002", 1300, 1400)
sdy_003 = cards.MonsterCard("Winged Dragon, Guardian of the Fortress #1", "SDY-003", 1400, 1200)
sdy_004 = cards.MonsterCard("Summoned Skull", "SDY-004", 2500, 1200)
sdy_005 = cards.MonsterCard("Beaver Warrior", "SDY-005", 1200, 1500)
sdy_006 = cards.MonsterCard("Dark Magician", "SDY-006", 2500, 2100)
sdy_007 = cards.MonsterCard("Gaia the Fierce Knight", "SDY-007", 2300, 2100)
sdy_008 = cards.MonsterCard("Curse of Dragon", "SDY-008", 2000, 1500)
sdy_009 = cards.MonsterCard("Celtic Guardian", "SDY-009", 1400, 1200)
sdy_010 = cards.MonsterCard("Mammoth Graveyard", "SDY-010", 1200, 800)

# Create Decks
test_cards = [sdy_001, sdy_002, sdy_003, sdy_004, sdy_005, sdy_006, sdy_007, sdy_008, sdy_009, sdy_010]
test_cards_2 = [sdy_001, sdy_002, sdy_003, sdy_004, sdy_005, sdy_006, sdy_007, sdy_008, sdy_009, sdy_010]

yugi_deck = cards.Deck(test_cards)
opp_deck = cards.Deck(test_cards_2)

# Create Players
yugi = player.ComputerPlayer("Yugi", yugi_deck)
opponent = player.ComputerPlayer("Opponent", opp_deck)

ygogame = game.Game(yugi, opponent)
ygogame.play_game()





