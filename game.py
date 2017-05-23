import pytest
import random
import collections
import enum

testPlayerName = "Alfred"

def die_roll():
    return random.randint(1,6)

class Player:
    def __init__(self, name):
        self.name = name
        self.establishments = {Card.WHEAT_FIELD: 1,
                               Card.BAKERY: 1}
        self.stash = 3

class EstablishmentIncomeRestriction(enum.Enum):
    SELF = enum.auto()
    OTHER = enum.auto()

class Establishment:
    def __init__(self, restriction = None, amount = 1):
        self.restriction = restriction
        self.amount = amount


class Card(enum.Enum):
    WHEAT_FIELD = Establishment()
    RANCH = Establishment()
    BAKERY = Establishment(EstablishmentIncomeRestriction.SELF)
    CONVENIENCE_STORE = Establishment(EstablishmentIncomeRestriction.SELF,3)
    CAFE = Establishment(EstablishmentIncomeRestriction.OTHER)

def initialize_player(name):
    return Player(name)

def initialize_marketplace():
    market =  {key : 6 for key in ["Apple Orchard",Card.BAKERY,"Cafe","Cheese Factory", "Convenience Store",
                                "Family Restaurant", "Forest", "Fruit and Vegetable Market", "Furniture Factory", "Mine",
                                Card.RANCH,Card.WHEAT_FIELD]}
    market2 = {key : 4 for key in ["Business Center", "Stadium", "TV Station"]}
    market.update(market2)
    return market

def income(playerToCheck, activePlayer, players, dieRoll):
    lossEstablishments = {3: [Card.CAFE]}
    gainEstablishments = {1: [Card.WHEAT_FIELD],
                          2: [Card.RANCH, Card.BAKERY], 
                          3: [Card.BAKERY],
                          4: [Card.CONVENIENCE_STORE]}
    # Losing Money to Other Players First
    lost = 0
    stolen = 0

    # How much active player loses
    for establishment in lossEstablishments.get(dieRoll,[]):
        for player in players:
            if player != activePlayer:
                lost += player.establishments.get(establishment,0)
        if playerToCheck != activePlayer:
            stolen += playerToCheck.establishments.get(establishment, 0)

    # Change in income is losses (down to zero but no lower)
    totalLosses = min(playerToCheck.stash, lost)

    # Then add income from gaining establishments
    totalGains = 0
    for establishment in gainEstablishments.get(dieRoll, []):
        if playerToCheck == activePlayer or establishment.value.restriction != EstablishmentIncomeRestriction.SELF:
            totalGains += playerToCheck.establishments.get(establishment, 0) * establishment.value.amount

    # Then add income from thievery
    totalGains += stolen

    return totalGains - totalLosses

# Tests
def test_die():
    rolls = [die_roll() for i in range(1000)]
    assert(max(rolls) == 6)
    assert(5 in rolls)
    assert(4 in rolls)
    assert(3 in rolls)
    assert(2 in rolls)
    assert(min(rolls) == 1)
    counts = collections.Counter(rolls)
    for key in counts.keys():
        assert(int(key) == key)

def test_initialize_player():
    playA = initialize_player(testPlayerName)
    # Player should have name
    assert(playA.name == testPlayerName)
    # Players should start with a single Wheat Field and a single Bakery
    assert(Card.WHEAT_FIELD in playA.establishments.keys())
    assert(playA.establishments[Card.WHEAT_FIELD] == 1)
    assert(Card.BAKERY in playA.establishments.keys())
    assert(playA.establishments[Card.BAKERY] == 1)
    assert(playA.stash == 3)

def test_initialize_marketplace():
    marketplace = initialize_marketplace()
    for establishment in ["Apple Orchard",Card.BAKERY,"Cafe","Cheese Factory", "Convenience Store",
        "Family Restaurant", "Forest", "Fruit and Vegetable Market", "Furniture Factory", "Mine",
        Card.RANCH,Card.WHEAT_FIELD]:
        assert(marketplace[establishment] == 6), "Market should start with 6 {}s".format(establishment)
    for specialEstablishment in ["Business Center", "Stadium", "TV Station"]:
        assert(marketplace[specialEstablishment] == 4), "Market should start with 4 {}s".format(specialEstablishment)

def test_income():
    playA = initialize_player(testPlayerName)
    playB = initialize_player("Bradley")

    players = [playA,playB]
    playA = reset_player(playA)
    playB = reset_player(playB)
    players = [playA,playB]
    playA.establishments[Card.WHEAT_FIELD] = 1
    assert(income(playA,playA,players,1) == 1)

    playA = reset_player(playA)
    players = [playA,playB]
    playA.establishments[Card.WHEAT_FIELD] = 2
    assert(income(playA,playA,players,1) == 2)

    playA = reset_player(playA)
    players = [playA,playB]
    playA.establishments[Card.RANCH] = 2
    assert(income(playA,playB,players,2) == 2)

    playA = reset_player(playA)
    players = [playA,playB]
    playA.establishments[Card.BAKERY] = 1
    assert(income(playA,playA,players,3) == 1)

    playA = reset_player(playA)
    playB = reset_player(playB)
    players = [playA,playB]
    playB.establishments[Card.BAKERY] = 1
    assert(income(playB,playA,players,3) == 0)

    playA = reset_player(playA)
    playB = reset_player(playB)
    players = [playA,playB]
    playA.establishments[Card.CONVENIENCE_STORE] = 1
    assert(income(playA,playA,players,4) == 3)
    
    playA = reset_player(playA)
    playB = reset_player(playB)
    players = [playA,playB]

    playB.stash = 10
    playA.establishments[Card.CAFE] = 2
    assert(income(playA,playB,players,3) == 2), "Cafe-related Thievery"
    print ("Pay attention NOW!")
    assert(income(playB,playB,players,3) == -2), "Player loses money upon rolling a 3 if another player has cafe(s)"
    playB.stash = 0
    assert(income(playB,playB,players,3) == 0)

    # 8-Ball's turn to write a failing test for Chrisantha

    playA = reset_player(playA)
    players = [playA,playB]
    playA.establishments[Card.BAKERY] = 2
    assert(income(playA,playA,players,2) == 2)

def reset_player(player):
    new_player = initialize_player(player.name)
    new_player.stash = 0
    new_player.establishments = {}
    return new_player


def main():
    test_initialize_marketplace()
    
if __name__ == '__main__':
    main()