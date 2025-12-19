from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
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
        # Create and arrange widgets and layout. Remove pass when complete.
        pass
        # TODO: Dealer Section with cards

        # TODO: Player Section with cards

        #  TODO: Buttons for hit, stand, new round

        #  TODO: Feedback

        #  TODO: Add widgets to layout

        #  TODO: Trigger a new layout with a new round


    # BUTTON ACTIONS

    def on_hit(self):
        # Player takes a card
        card = self.game.player_hit()
        self.add_card(self.playerCardsLayout, card)

        if self.game.player_total() > 21:
          # TODO: what should happen if a player goes over 21? Remove pass when complete
          pass

    def on_stand(self):
        # TODO: Player ends turn; dealer reveals their hidden card and plays. Remove pass when complete
        pass

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
