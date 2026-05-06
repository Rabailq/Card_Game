import random # For shuffling cards #
import json # Used for saving and loading game #
import os # Editing contents of directories #

class Card:
  def __init__(self, suit, value):
    self.suit = suit # Stores card suits #
    self.value = value # Stores card values #

  def rank_value(self):
    rank_mapping = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,"10": 10, "Jack": 11, "Queen": 12, "King": 13, "Ace": 14
    }
    return rank_mapping.get(self.value, 0) # Return 0 if value not found #

  def is_joker(self): # Checks if a card is joker #
    return self.value.lower() == "joker"

  def to_dict(self):
    return {"suit": self.suit, "value": self.value}

  @classmethod
  def from_dict(cls, data):
    return cls(data["suit"], data["value"])
class Deck:
  SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"] # All possible suits #
  VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "King", "Queen", "Jack", "Ace"] # All possible values #

  def __init__(self):
    self.cards = [Card(suit, value) for suit in self.SUITS for value in self.VALUES] # Generate all cards #

    # Adding two jokers to deck #
    self.cards.append(Card(None, "Joker"))
    self.cards.append(Card(None, "Joker"))

    random.shuffle(self.cards) # Shuffling all cards #

  def deal_cards(self):
    # Split deck into two equal halves for both players #
    half_index = len(self.cards) // 2
    return self.cards[:half_index], self.cards[half_index:]

  def to_dict(self):
    return {"cards": [card.to_dict() for card in self.cards]}

  @classmethod
  def from_dict(cls, data):
    loaded_cards = [Card.from_dict(card_data) for card_data in data["cards"]]
    deck = cls()  # Create an empty deck
    deck.cards = loaded_cards  # Assign the loaded cards to the deck
    return deck


class Player:
  def __init__(self, name):
    self.name = name
    self.cards_in_hand = [] # List that stores card objects currently held by players #
    self.points = 0 # Player's default score #

  def draw_card(self):
    if self.cards_in_hand: # Checks if list of cards in hand is not empty #
      return self.cards_in_hand.pop(0)
    else:
      return None

  def receive_cards(self, cards):
    self.cards_in_hand.extend(cards) # Adding cards to player's hand #

  def to_dict(self):
    return {"name": self.name, "cards_in_hand": [card.to_dict() for card in self.cards_in_hand], "points": self.points
    }

  @classmethod
  def from_dict(cls, data):
    player = cls(data["name"])
    player.cards_in_hand = [Card.from_dict(card_data) for card_data in data["cards_in_hand"]]
    player.points = data["points"]
    return player

class Game:
  def __init__(self):
    self.deck = Deck()
    self.player_one = None
    self.player_two = None
    self.round_limit = 0
    self.current_round = 0
    self.save_file_path = "saved_game.json" # Default saved file #

  def card_display(self, card):
    return "Joker" if card.is_joker() else f"{card.value} of {card.suit}"

  def setup_game(self):
    print ("Welcome to Python Card War!")
    print ("Game Rules:")
    print ("Joker: -1 point")
    print ("King: +1 point bonus")
    print ("Queen: both players swap all remaining cards")
    print ("Equal rank cards: WAR!")

    name_one = input("Enter Player 1 name: ")
    name_two = input("Enter Player 2 name: ")
    self.round_limit = int(input("Enter total number of rounds: "))

    self.player_one = Player(name_one)
    self.player_two = Player(name_two)

    cards_one, cards_two = self.deck.deal_cards()
    self.player_one.receive_cards(cards_one)
    self.player_two.receive_cards(cards_two)

  def save_game(self):
    # Save current game to JSON file #
    game_data = {
    "player_one": self.player_one.to_dict(),
    "player_two": self.player_two.to_dict(),
    "current_round": self.current_round,
    "round_limit": self.round_limit,
    "deck": self.deck.to_dict()
    }

    with open(self.save_file_path, "w") as save_file:
      json.dump(game_data, save_file)
    print ("Game saved successfully!")

  def load_game(self):
    try:
      with open(self.save_file_path, "r") as file:
        data = json.load(file)
        self.player_one = Player.from_dict(data["player_one"])
        self.player_two = Player.from_dict(data["player_two"])
        self.current_round = data["current_round"]
        self.round_limit = data["round_limit"]
        self.deck = Deck.from_dict(data["deck"])
        print ("Game loaded successfully!")
    except FileNotFoundError:
      print ("No saved game found. Starting a new game.")
      self.setup_game()

  def compare_cards(self, card_one, card_two):
    if card_one.is_joker():
      self.player_one.points -= 1
    if card_two.is_joker():
      self.player_two.points -= 1

    if card_one.value == "King":
      self.player_one.points += 1
    if card_two.value == "King":
      self.player_two.points += 1

    if card_one.value == "Queen" or card_two.value == "Queen":
        if self.player_one.cards_in_hand and self.player_two.cards_in_hand:
            print ("Queen drawn. Both players swap all their remaining cards!")
            self.player_one.cards_in_hand, self.player_two.cards_in_hand = (
            self.player_two.cards_in_hand,
            self.player_one.cards_in_hand,
            )
            return
# WAR rule #

    value_one = card_one.rank_value()
    value_two = card_two.rank_value()

    if value_one == value_two:
      print("WAR!")

      if len(self.player_one.cards_in_hand) < 2 or len(self.player_two.cards_in_hand) < 2:
        print("  Not enough cards for War! Round is a draw.")
        return
      print("  Each player places one card face down...")
      self.player_one.cards_in_hand.pop(0)
      self.player_two.cards_in_hand.pop(0)
      war_card_one = self.player_one.cards_in_hand.pop(0)
      war_card_two = self.player_two.cards_in_hand.pop(0)
      print(f"{self.player_one.name} plays: {self.card_display(war_card_one)}")
      print(f"{self.player_two.name} plays: {self.card_display(war_card_two)}")

      if war_card_one.rank_value() > war_card_two.rank_value():
       print(f"{self.player_one.name} wins the WAR!")
       self.player_one.points += 2
      elif war_card_two.rank_value() > war_card_one.rank_value():
       print(f"{self.player_two.name} wins the WAR!")
       self.player_two.points += 2
      else:
       print("WAR is a draw! No points awarded.")
      return

    if value_one > value_two:
      self.player_one.points += 1
    elif value_two > value_one:
      self.player_two.points += 1

  def play_game(self):
    while self.current_round < self.round_limit:
      card_one = self.player_one.draw_card()
      card_two = self.player_two.draw_card()

      if not card_one or not card_two:
        print ("No more cards left to draw!")
        break

      print(f"\nRound {self.current_round + 1}:")
      print(f"{self.player_one.name} draws {card_one.value} of {card_one.suit}")
      print(f"{self.player_two.name} draws {card_two.value} of {card_two.suit}")

      self.compare_cards(card_one, card_two)
      self.current_round += 1

      user_choice = input ("Press Enter to continue, 'S' to save, or 'Q' to quit: ").upper()
      if user_choice == "S":
        self.save_game()
        print("You can resume later!")
        break
      elif user_choice == "Q":
        print("Game exited.")
        return

    self.display_final_winner()

  def display_final_winner(self):
    print ("\nFinal Score:")
    print (f"{self.player_one.name}: {self.player_one.points} points")
    print (f"{self.player_two.name}: {self.player_two.points} points")

    if self.player_one.points > self.player_two.points:
      print (f"Winner: {self.player_one.name}")
    elif self.player_two.points > self.player_one.points:
      print (f"Winner: {self.player_two.name}")
    else:
      print ("It's a tie!")

  def start(self):
    option = input ("Do you want to (N)ew game or (L)oad saved game? ").upper()
    if option == "L":
      self.load_game()
    if self.player_one and self.player_two:
          self.play_game()
    else:
      self.setup_game()
      self.play_game()

if __name__ == "__main__":
  game = Game()
  game.start()
