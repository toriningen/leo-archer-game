import random


class Unit:
    for_sale = False
    cost = 0
    base_hp = 20
    armor = 0
    damage = 0

    def __init__(self, owner):
        self.owner = owner
        self.hp = self.base_hp

    def is_alive(self):
        return self.hp > 0

    def harm(self, damage):
        real_damage = damage - self.armor
        if real_damage < 0:
            real_damage = 0

        self.hp -= real_damage
        if self.hp <= 0:
            self.on_died()

    def on_turn(self):
        ...

    def on_died(self):
        self.owner.on_unit_died(self)

    def __repr__(self):
        return f'<{type(self).__name__} hp={self.hp}/{self.base_hp} def={self.armor} atk={self.damage}>'


class Castle(Unit):
    for_sale = False
    base_hp = 100

    def on_died(self):
        super().on_died()
        self.owner.on_castle_destroyed()


class Farmer(Unit):
    for_sale = True
    cost = 5

    def on_turn(self):
        self.owner.gold += 1


class Archer(Unit):
    for_sale = True
    cost = 20
    damage = 10
    armor = 1

    def on_turn(self):
        enemy = self.owner.get_random_alive_enemy()
        if enemy is not None:
            enemy.harm(self.damage)


class Knight(Unit):
    for_sale = True
    cost = 30
    damage = 3
    armor = 5

    def on_turn(self):
        enemy = self.owner.get_random_alive_enemy()
        if enemy is not None:
            enemy.harm(self.damage)


class Player:
    def __init__(self, game, name):
        self.game = game
        self.name = name

        self.gold = 5

        self.bought_times = {}
        self.castle = Castle(self)
        self.units = [
            self.castle
        ]

    def __repr__(self):
        return f'<Player {self.name} gold={self.gold}>'

    def is_defeated(self):
        return not self.castle.is_alive()

    def get_unit_cost(self, unit_type):
        return round(unit_type.cost * (1.2 ** self.bought_times.get(unit_type, 0)))

    def can_buy_unit(self, unit_type):
        if not issubclass(unit_type, Unit):
            raise TypeError("not unit")

        if not unit_type.for_sale:
            raise TypeError("unit is not for sale")

        real_cost = self.get_unit_cost(unit_type)

        if self.gold < real_cost:
            return False

        return True

    def buy_unit(self, unit_type):
        if not self.can_buy_unit(unit_type):
            raise ValueError("cannot buy unit")

        self.gold -= self.get_unit_cost(unit_type)
        self.units.append(unit_type(self))
        self.bought_times[unit_type] = self.bought_times.get(unit_type, 0) + 1

    def on_turn(self):
        for unit in self.units:
            unit.on_turn()

    def on_unit_died(self, unit):
        self.units.remove(unit)

    def on_castle_destroyed(self):
        print(self, '?????????? ????????????????')

    def get_random_alive_enemy(self):
        enemy_units = [unit
                       for player in self.game.players
                       if player is not self
                       for unit in player.units
                       if unit.is_alive()]

        if not enemy_units:  # ???????????? ???? ????????????????
            return None

        return random.choice(enemy_units)

    def decide(self):
        ...


class HumanPlayer(Player):
    def ask_unit_to_buy(self):
        while True:
            farmer_cost = self.get_unit_cost(Farmer)
            archer_cost = self.get_unit_cost(Archer)
            knight_cost = self.get_unit_cost(Knight)

            who = input(
                f'???????? {self.gold} ??????????, ???????? ????????????? (enter - ????????????, 1 - ???????????? ({farmer_cost}), 2 - ???????????? ({archer_cost}), 3 - ???????????? ({knight_cost})) >')
            if not who:
                return None
            elif who == '1':
                return Farmer
            elif who == '2':
                return Archer
            elif who == '3':
                return Knight

            print('?????????????????? ??????????, ?????????????? ?????? ??????.')

    def decide(self):
        while True:
            unit_type = self.ask_unit_to_buy()
            if unit_type is None:
                return

            if not self.can_buy_unit(unit_type):
                print('?????????? ??????, ???? ???? ??????????????????')
                continue

            self.buy_unit(unit_type)
            print('????????????, ?????? ??????-?????')


class ComputerPlayer(Player):
    def __init__(self, game, name):
        super().__init__(game, name)
        self.want_this_unit = Farmer

    def want_another_random_unit(self):
        self.want_this_unit = random.choice([Farmer, Archer, Knight])

    def decide(self):
        # ?????????? ?????????????????? - ???????????? ???????????? ?????????? ???????? ?????????? ?? ?????????? ???? ???????? ??????????
        if self.can_buy_unit(self.want_this_unit):
            self.buy_unit(self.want_this_unit)
            self.want_another_random_unit()


class Game:
    def __init__(self):
        self.human_player = HumanPlayer(self, "Human")
        self.computer_players = [
            ComputerPlayer(self, "Alice"),
            ComputerPlayer(self, "Bob"),
        ]
        self.players = [
            self.human_player,
            *self.computer_players,
        ]

    def make_turn(self):
        for player in self.players:
            if not player.is_defeated():
                player.on_turn()

    def decide(self):
        for player in self.players:
            if not player.is_defeated():
                player.decide()

    def render(self):
        # ??????????, ?????????? ?????? ????????
        print('=====')
        for player in self.players:
            print(player)
            for unit in player.units:
                print('->', unit)
            print()

    def human_defeated(self):
        return self.human_player.is_defeated()

    def human_won(self):
        return len([player for player in self.computer_players if not player.is_defeated()]) == 0


if __name__ == '__main__':
    g_game = Game()

    while True:
        g_game.make_turn()
        g_game.render()

        if g_game.human_defeated():
            g_game.render()
            print('=== ???? ??????????????????')
            break

        if g_game.human_won():
            g_game.render()
            print('=== ???? ????????????????!')
            break

        g_game.decide()

