import random

class Game21:
    def __init__(self):
        # Start immediately with a fresh round
        self.new_round()

    # ROUND MANAGEMENT

    def new_round(self):
        """
        Prepares for a new round
        Suggested process:
        - Create and shuffle a new deck
        - Reset card pointer
        - Empty both hands
        - Reset whether the dealer's hidden card has been revealed
        """
        self.deck = self.create_deck()
        random.shuffle(self.deck)

        # Instead of removing cards from the deck,
        # we keep an index of the "next card" to deal.
        self.deck_position = 0

        # Hands start empty; cards will be dealt after UI calls deal_initial_cards()
        self.player_hand = []
        self.dealer_hand = []

        # The first dealer card starts hidden until Stand is pressed
        self.dealer_hidden_revealed = False

    def deal_initial_cards(self):
        """
        Deal two cards each to player and dealer.
        """
        self.player_hand = [self.draw_card(), self.draw_card()]
        self.dealer_hand = [self.draw_card(), self.draw_card()]

    # DECK AND CARD DRAWING

    def create_deck(self):
        """
        Create a standard 52-card deck represented as text strings, e.g.:
        'A♠', '10♥', 'K♦'.

        Ranks: A, 2–10, J, Q, K
        Suits: spades, hearts, diamonds, clubs (with unicode symbols)
        """
        ranks = ["A"] + [str(n) for n in range(2, 11)] + ["J", "Q", "K"]
        suits = ["♠", "♥", "♦", "♣"]
        return [f"{rank}{suit}" for rank in ranks for suit in suits]

    def draw_card(self):
        """
        Return the next card in the shuffled deck.
        """
        card = self.deck[self.deck_position]
        self.deck_position += 1
        return card

    # HAND VALUES + ACE HANDLING

    def card_value(self, card):
        """
        Convert a card string into its numeric value.

        Rules:
        - Number cards = their number (2–10)
        - J, Q, K = 10
        - A is normally 11, may later count as 1 if needed
        """
        rank = card[:-1]  # everything except the suit symbol

        if rank in ["J", "Q", "K"]:
            return 10

        if rank == "A":
            return 11  # Initially treat Ace as 11

        # Otherwise it's a number from 2 to 10
        return int(rank)

    def hand_total(self, hand):
        """
        Calculates the best possible total for a hand.
        Aces are counted as 11 unless this would bust the hand,
        in which case they are reduced to 1.

        Suggested Process:
        1. Count all Aces as 11 initially.
        2. If total > 21, subtract 10 for each Ace, so it effectively makes them = 1
        """
        total = 0
        aces = 0

        for card in hand:
            v = self.card_value(card)
            total += v
            if card[:-1] == "A":
                aces += 1

        # If we bust, downgrade Aces from 11 to 1 by subtracting 10 per Ace as needed
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    # PLAYER ACTIONS

    def player_hit(self):
        card = self.draw_card()
        self.player_hand.append(card)
        return card

    def player_total(self):
        return self.hand_total(self.player_hand)

    # DEALER ACTIONS

    def reveal_dealer_card(self):
        self.dealer_hidden_revealed = True


    def dealer_total(self):
        return self.hand_total(self.dealer_hand)

    def play_dealer_turn(self):
        drawn = []
        # Dealer hits while total is less than 17
        while self.dealer_total() < 17:
            card = self.draw_card()
            self.dealer_hand.append(card)
            drawn.append(card)
        return drawn

    # WINNER DETERMINATION

    def decide_winner(self):
        player = self.player_total()
        dealer = self.dealer_total()

        if player > 21:
            return "Player busts. Dealer wins!"
        if dealer > 21:
            return "Dealer busts. Player wins!"

        if player > dealer:
            return "Player wins!"
        if dealer > player:
            return "Dealer wins!"
        return "Push (tie)."


