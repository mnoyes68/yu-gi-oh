import player
import cards
import json

def write_game_state(player, opponent):
    game_state = {}

    # Player Info
    game_state['PlayerLP'] = player.life_points
    game_state['PlayerHandSize'] = len(player.hand.cards)
    game_state['PlayerMonstersOnBoard'] = player.board.get_occupied_monster_spaces()
    game_state['PlayerDeckSize'] = len(player.deck.cards)
    game_state['OppLP'] = opponent.life_points
    game_state['OppHandSize'] = len(opponent.hand.cards)
    game_state['OppMonstersOnBoard'] = opponent.board.get_occupied_monster_spaces()
    game_state['OppDeckSize'] = len(opponent.deck.cards)
    
    # Player Board Info
    player_monsters = player.board.get_monsters()
    for i in range(0, 5):
        prefix = "PlayerMonster" + str(i+1)
        if i < len(player_monsters):
            monster = player_monsters[i]
            monster_state = write_monster_card(monster)
            game_state[prefix] = monster_state
        else:
            monster_state = write_monster_card(None)
            game_state[prefix] = monster_state

    # Opponent Board Info
    opp_monsters = opponent.board.get_monsters()
    for i in range(0, 5):
        prefix = "OpponentMonster" + str(i+1)
        if i < len(opp_monsters):
            monster = opp_monsters[i]
            monster_state = write_monster_card(monster)
            game_state[prefix] = monster_state
        else:
            monster_state = write_monster_card(None)
            game_state[prefix] = monster_state

    return game_state


def write_monster_card(monster):
    card_state = {}
    if monster != None:
        card_state['Exists'] = 1
        card_state['Attack'] = monster.atk
        card_state['Defense'] = monster.defn
        card_state['Level'] = monster.level
        if(monster.attacked_this_turn):
            card_state['AttackedThisTurn'] = 1
        else:
            card_state['AttackedThisTurn'] = 0
        return card_state
    else:
        card_state['Exists'] = 0
        card_state['Attack'] = 0
        card_state['Defense'] = 0
        card_state['Level'] = 0
        card_state['AttackedThisTurn'] = 0
        return card_state

