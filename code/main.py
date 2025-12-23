from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt6.QtCore import Qt
import sys

# this project should use a modular approach - try to keep UI logic and game logic separate
from game_logic import Game21

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game of 21")

        # set the windows dimensions
        self.setGeometry(200, 200, 400, 400)

        self.game = Game21()

        self.initUI()

    def initUI(self):
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox

        central = QWidget()
        self.setCentralWidget(central)

        self.mainLayout = QVBoxLayout(central)
        self.mainLayout.setSpacing(12)

        # Dealer Section
        dealerBox = QGroupBox("Dealer")
        dealerLayout = QVBoxLayout(dealerBox)

        self.dealerTotalLabel = QLabel("Total: ?")
        self.dealerTotalLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.dealerCardsLayout = QHBoxLayout()
        self.dealerCardsLayout.setSpacing(10)

        # --- Player Section ---
        playerBox = QGroupBox("Player")
        playerLayout = QVBoxLayout(playerBox)

        self.playerTotalLabel = QLabel("Total: 0")
        self.playerTotalLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.playerCardsLayout = QHBoxLayout()
        self.playerCardsLayout.setSpacing(10)

        playerLayout.addWidget(self.playerTotalLabel)
        playerLayout.addLayout(self.playerCardsLayout)



    # BUTTON ACTIONS

    def on_hit(self):
        # Player takes a card
        card = self.game.player_hit()
        self.add_card(self.playerCardsLayout, card)

        if self.game.player_total() > 21:
            self.feedbackLabel.setText("You busted! Dealer wins.")
            # Reveal dealer card so totals make sense at the end
            self.game.reveal_dealer_card()
            self.update_dealer_cards(full=True)
            self.update_totals(full_dealer=True)
            self.end_round()
        else:
            self.update_totals(full_dealer=False)

    def on_stand(self):
        # Player ends turn; dealer reveals and plays
        self.game.reveal_dealer_card()
        self.update_dealer_cards(full=True)

        # Dealer hits until 17+
        drawn = self.game.play_dealer_turn()
        for card in drawn:
            self.add_card(self.dealerCardsLayout, card)

        # Decide winner
        message = self.game.decide_winner()
        self.feedbackLabel.setText(message)

        # Update totals and lock controls
        self.update_totals(full_dealer=True)
        self.end_round()


    def on_new_round(self):
        self.game.new_round()
        self.new_round_setup()

    # HELPER METHODS

    def clear_layout(self, layout):
        # Remove all widgets from a layout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def add_card(self, layout, card_text):
        # Create a QLabel showing the card value and add it to the chosen layout.
        label = QLabel(card_text)
        layout.addWidget(label)
        label.setProperty("card", True)

    def update_dealer_cards(self, full=False):
        # Show dealer cards; hide the first card until revealed
        self.clear_layout(self.dealerCardsLayout)

        for i, card in enumerate(self.game.dealer_hand):
            if i == 0 and not full:
                self.add_card(self.dealerCardsLayout, "??")   # face-down
            else:
                self.add_card(self.dealerCardsLayout, card)

        # TODO: update relevant labels in response to dealer actions. Remove pass when complete
        if full:
            pass
        else:
            pass

    def new_round_setup(self):
        # TODO: Prepare a fresh visual layout

        # TODO: update relevant labels (reset dealer and player totals)

        # TODO: display new cards for dealers and players

        # TODO: enable buttons for Stand and Hit - Remove pass when complete
        pass


    def end_round(self):
        # TODO: Disable button actions after the round ends. Remove pass when complete
        pass


# complete

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # macOS only fix for icons appearing
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
