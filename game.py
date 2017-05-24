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
        
    def __repr__(self):
        return self.name

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

def gains(playerToCheck, activePlayer, dieRoll):
    gainEstablishments = {1: [Card.WHEAT_FIELD],
                          2: [Card.RANCH, Card.BAKERY], 
                          3: [Card.BAKERY],
                          4: [Card.CONVENIENCE_STORE]}
    totalGains = 0

    for establishment in gainEstablishments.get(dieRoll, []):
        if playerToCheck == activePlayer or establishment.value.restriction != EstablishmentIncomeRestriction.SELF:
            totalGains += playerToCheck.establishments.get(establishment, 0) * establishment.value.amount

    return totalGains

def stolen(playerToCheck, robbedPlayer, dieRoll):
    stealEstablishments = {3: [Card.CAFE]}
    amountStolen = 0
    for establishment in stealEstablishments.get(dieRoll, []):
         amountStolen += playerToCheck.establishments.get(establishment, 0)
    amountStolen = min(amountStolen, robbedPlayer.stash)
    return amountStolen

# here, the "players" list is counterclockwise around the table (reverse turn order)
def income(playerToCheck, activePlayer, players, dieRoll):
    lossEstablishments = {3: [Card.CAFE]}
    gainEstablishments = {1: [Card.WHEAT_FIELD],
                          2: [Card.RANCH, Card.BAKERY], 
                          3: [Card.BAKERY],
                          4: [Card.CONVENIENCE_STORE]}
    # Losing Money to Other Players First
    lost = 0

    amountStolen = 0

    # How much active player loses
    # This should be handled by the calling context. Shouldn't explicitly count everyone here
    # Just need to get the tests to pass in this refactor for now
    if playerToCheck == activePlayer:
        for player in players:
            if player != activePlayer:
                lost += stolen(player, activePlayer, dieRoll)
    else:
        amountStolen = stolen(playerToCheck, activePlayer, dieRoll)

    # Change in income is losses (down to zero but no lower)
    totalLosses = min(playerToCheck.stash, lost)
    totalStolen = min(activePlayer.stash, amountStolen)

    # Then add income from thievery
    totalGains = gains(playerToCheck, activePlayer, dieRoll) + totalStolen

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

    playA = reset_player(playA)
    
    playA.establishments[Card.WHEAT_FIELD] = 1
    assert(gains(playA,playA,1) == 1)

    
    playA.establishments[Card.WHEAT_FIELD] = 2
    assert(gains(playA,playA,1) == 2)

    
    playA.establishments[Card.RANCH] = 2
    assert(gains(playA,playB,2) == 2)

    
    playA.establishments[Card.BAKERY] = 1
    assert(gains(playA,playA,3) == 1)

    playA = reset_player(playA)
    
    playB.establishments[Card.BAKERY] = 1
    assert(gains(playB,playA,3) == 0)

    playA = reset_player(playA)
    
    playA.establishments[Card.CONVENIENCE_STORE] = 1
    assert(gains(playA,playA,4) == 3)
    
    playA = reset_player(playA)
    

    playB.stash = 10
    playA.establishments[Card.CAFE] = 2
    assert(stolen(playA,playB,3) == 2), "Cafe-related Thievery"
    playB.stash = 0
    assert(stolen(playA,playB,3) == 0), "Player can't lose more than they have"
    playB.stash = 1
    assert(stolen(playA,playB,3) == 1), "Player loses only as much as they have"

    playA = reset_player(playA)
    

    playA.stash = 0
    playB.establishments[Card.CAFE] = 3
    assert(stolen(playB,playA, 3) == 0), "Player should not take money if active player has no money to take"

    
    playA.establishments[Card.BAKERY] = 2
    assert(gains(playA,playA,2) == 2)

    # What happens if a player's roll results in both a Bakery and a Cafe being triggered?
    playA = reset_player(playA)
    playB = reset_player(playB)
    playC = reset_player(initialize_player("Curmudgeon"))
    
    playB.establishments[Card.CAFE] = 3
    playA.establishments[Card.BAKERY] = 2
    playC.establishments[Card.CAFE] = 1
    playA.stash = 1
    assert(stolen(playB, playA, 3) == 1), "playB steals from playA"
    playA.stash = 0
    assert(stolen(playC, playA, 0) == 0), "playC gets nothing after playA already loses all moneys"
    assert(gains(playA, playA, 3) == 2), "Player gets money from their bakeries"


def reset_player(player):
    new_player = initialize_player(player.name)
    new_player.stash = 0
    new_player.establishments = {}
    return new_player


def main():
    test_initialize_marketplace()
    
if __name__ == '__main__':
    main()