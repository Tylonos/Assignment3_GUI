from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QSizePolicy
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtCore import Qt
import sys

from pathlib import Path

# this project should use a modular approach - try to keep UI logic and game logic separate
from game_logic import Game21

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game of 21")

        # set the windows dimensions
        self.setGeometry(200, 200, 400, 400)

        self.game = Game21()
        self.cards_dir = Path(__file__).resolve().parent / "assets" / "cards"
        self.card_min_size = (90, 130)  # minimal (width, height)
        self.card_size = self.card_min_size

        self.is_dark = False

        # App-wide stylesheets (kept simple)
        self.light_qss = """
            QWidget { background: #ffffff; color: #111; }
            QGroupBox {
                border: 1px solid #cfcfcf;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                font-weight: bold;
            }
            QLabel { font-size: 13px; }
            QPushButton {
                border: 1px solid #444;
                font-weight: bold;
                padding: 6px 14px;
                background-color: #f5f5f5;
            }
            QPushButton:focus {
                outline: none;
            }
            QPushButton:hover { background-color: #e6e6e6; }
            QPushButton:disabled {
                color: #999;
                border: 1px solid #aaa;
                background-color: #f0f0f0;
            }
        """

        self.dark_qss = """
            QWidget { background: #121212; color: #eee; }
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                font-weight: bold;
                color: #eee;
            }
            QLabel { font-size: 13px; }
            QPushButton {
                border: 1px solid #888;
                font-weight: bold;
                padding: 6px 14px;
                background-color: #1f1f1f;
                color: #eee;
            }
            QPushButton:focus {
                outline: none;
            }
            QPushButton:hover { background-color: #2a2a2a; }
            QPushButton:disabled {
                color: #777;
                border: 1px solid #555;
                background-color: #1a1a1a;
            }
        """

        self.initUI()

    def initUI(self):
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox

        central = QWidget()
        self.setCentralWidget(central)

        self.mainLayout = QVBoxLayout(central)
        self.mainLayout.setSpacing(12)

        #  Menu bar: theme toggle 
        view_menu = self.menuBar().addMenu("View")
        self.themeAction = QAction("Dark mode", self)
        self.themeAction.setCheckable(True)
        self.themeAction.setChecked(self.is_dark)
        self.themeAction.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.themeAction)

        # Dealer Section
        dealerBox = QGroupBox("Dealer")
        dealerLayout = QVBoxLayout(dealerBox)

        self.dealerTotalLabel = QLabel("Total: ?")
        self.dealerTotalLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.dealerCardsLayout = QHBoxLayout()
        self.dealerCardsLayout.setSpacing(10)

        dealerLayout.addWidget(self.dealerTotalLabel)
        dealerLayout.addLayout(self.dealerCardsLayout)

        #  Player Section 
        playerBox = QGroupBox("Player")
        playerLayout = QVBoxLayout(playerBox)

        self.playerTotalLabel = QLabel("Total: 0")
        self.playerTotalLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.playerCardsLayout = QHBoxLayout()
        self.playerCardsLayout.setSpacing(10)

        playerLayout.addWidget(self.playerTotalLabel)
        playerLayout.addLayout(self.playerCardsLayout)

        #  Scoreboard + Feedback 
        self.scoreboardLabel = QLabel("Scoreboard — Player: 0 | Dealer: ?")
        self.scoreboardLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.feedbackLabel = QLabel("Press New Round to start")
        self.feedbackLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedbackLabel.setWordWrap(True)

        #  Controls 
        controlsBox = QGroupBox("Controls")
        controlsLayout = QHBoxLayout(controlsBox)

        self.hitButton = QPushButton("Hit")
        self.standButton = QPushButton("Stand")
        self.newRoundButton = QPushButton("New Round")

        # Prevent buttons from stretching and hiding the checkbox on small widths
        for b in (self.hitButton, self.standButton, self.newRoundButton):
            b.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.hitButton.clicked.connect(self.on_hit)
        self.standButton.clicked.connect(self.on_stand)
        self.newRoundButton.clicked.connect(self.on_new_round)

        controlsLayout.addWidget(self.hitButton)
        controlsLayout.addWidget(self.standButton)
        controlsLayout.addWidget(self.newRoundButton)

        # Add to main layout
        self.mainLayout.addWidget(dealerBox)
        self.mainLayout.addWidget(playerBox)
        self.mainLayout.addWidget(self.scoreboardLabel)
        self.mainLayout.addWidget(self.feedbackLabel)
        self.mainLayout.addWidget(controlsBox)

        self.apply_theme()
        # Start first round immediately
        self.new_round_setup()

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
        """Add a card widget to the given layout. Uses an image if available, else falls back to text."""
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        label.setProperty("card_text", card_text)

        pix = self.card_pixmap(card_text)
        if pix is not None:
            self.apply_card_pixmap(label, card_text)
        else:
            # Fallback to readable text
            label.setText(card_text)
            label.setMinimumWidth(60)
            label.setMinimumHeight(40)
            label.setStyleSheet("""
                QLabel {
                    padding: 6px;
                    font-size: 14px;
                    border: 1px solid #888;
                    border-radius: 6px;
                    background: white;
                }
            """)

        self.recompute_card_size()
        layout.addWidget(label)
        label.setProperty("card", True)

    def card_pixmap(self, card_text: str):
        """Return a QPixmap for a card like 'A♠' if an image exists, else None."""
        path = self.resolve_card_image_path(card_text)
        if path is None:
            return None
        pix = QPixmap(str(path))
        if pix.isNull():
            return None
        return pix

    def resolve_card_image_path(self, card_text: str):
        """Try several filename conventions for the given card_text."""
        if not self.cards_dir.exists():
            return None

        # Dealer back image support
        if card_text == "??":
            for name in ("back.png", "card_back.png", "BACK.png"):
                p = self.cards_dir / name
                if p.exists():
                    return p
            return None

        # Split rank/suit from text representation
        suit_char = card_text[-1]
        rank = card_text[:-1]

        suit_map = {"♠": "S", "♥": "H", "♦": "D", "♣": "C"}
        suit_letter = suit_map.get(suit_char, "")

        candidates = []

        # 1) rank+suitLetter
        if suit_letter:
            candidates.append(f"{rank}{suit_letter}.png")
            candidates.append(f"{rank}_{suit_letter}.png")
            candidates.append(f"{rank}{suit_letter}.jpg")
            candidates.append(f"{rank}_{suit_letter}.jpg")

        # 2) unicode suit in filename
        candidates.append(f"{rank}{suit_char}.png")
        candidates.append(f"{rank}{suit_char}.jpg")

        # 3) lower-case variants
        if suit_letter:
            candidates.append(f"{rank}{suit_letter.lower()}.png")
            candidates.append(f"{rank}_{suit_letter.lower()}.png")

        for filename in candidates:
            p = self.cards_dir / filename
            if p.exists():
                return p

        return None

    def recompute_card_size(self):
        """Compute a target card size based on current window width, but never below the minimum."""
        min_w, min_h = self.card_min_size

        # Available width inside the central widget
        cw = self.centralWidget().width() if self.centralWidget() else self.width()
        available = max(200, cw - 60)  # padding for margins/groupboxes

        # Estimate how many cards we need to fit on the widest row
        dealer_n = max(2, len(getattr(self.game, "dealer_hand", [])))
        player_n = max(2, len(getattr(self.game, "player_hand", [])))
        n = max(dealer_n, player_n)

        spacing = 10
        total_spacing = spacing * (n - 1)
        per_card_w = (available - total_spacing) / n if n > 0 else min_w

        # Clamp to at least minimum; cap a bit so they don't become huge
        w = int(max(min_w, min(200, per_card_w)))
        h = int(w * (min_h / min_w))

        self.card_size = (w, h)

        # Apply to existing card widgets
        self.rescale_cards_in_layout(self.dealerCardsLayout)
        self.rescale_cards_in_layout(self.playerCardsLayout)

    def rescale_cards_in_layout(self, layout):
        if layout is None:
            return
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if isinstance(w, QLabel):
                card_text = w.property("card_text")
                if not card_text:
                    continue
                pix = self.card_pixmap(card_text)
                if pix is not None:
                    self.apply_card_pixmap(w, card_text)
                else:
                    # Text fallback: still keep a consistent box size
                    cw, ch = self.card_size
                    w.setMinimumSize(max(60, cw), max(40, ch))

    def apply_card_pixmap(self, label: QLabel, card_text: str):
        """Set (and scale) a pixmap for the given label using the current card_size."""
        pix = self.card_pixmap(card_text)
        if pix is None:
            return
        w, h = self.card_size
        label.setPixmap(
            pix.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )
        label.setFixedSize(w, h)

    def update_totals(self, full_dealer: bool):
        # Player total is always visible
        p = self.game.player_total()
        self.playerTotalLabel.setText(f"Total: {p}")

        # Dealer total depends on reveal state
        if full_dealer:
            d = self.game.dealer_total()
            self.dealerTotalLabel.setText(f"Total: {d}")
            self.scoreboardLabel.setText(f"Scoreboard — Player: {p} | Dealer: {d}")
        else:
            self.scoreboardLabel.setText(f"Scoreboard — Player: {p} | Dealer: ?")

    def update_dealer_cards(self, full=False):
        # Show dealer cards; hide the first card until revealed
        self.clear_layout(self.dealerCardsLayout)

        for i, card in enumerate(self.game.dealer_hand):
            if i == 0 and not full:
                self.add_card(self.dealerCardsLayout, "??")   # face-down
            else:
                self.add_card(self.dealerCardsLayout, card)

        # Update dealer total label depending on whether the hidden card is revealed
        if full:
            self.dealerTotalLabel.setText(f"Total: {self.game.dealer_total()}")
        else:
            # Show only the visible (second) card total while the first is hidden
            if len(self.game.dealer_hand) >= 2:
                visible_only = [self.game.dealer_hand[1]]
                self.dealerTotalLabel.setText(f"Total: {self.game.hand_total(visible_only)}")
            else:
                self.dealerTotalLabel.setText("Total: ?")

        self.recompute_card_size()

    def new_round_setup(self):
        # Clear previous cards
        self.clear_layout(self.dealerCardsLayout)
        self.clear_layout(self.playerCardsLayout)

        # Deal a fresh round
        self.game.deal_initial_cards()
        self.recompute_card_size()

        # Show cards (dealer first card hidden)
        self.update_dealer_cards(full=False)
        for card in self.game.player_hand:
            self.add_card(self.playerCardsLayout, card)

        # Update totals and UI state
        self.update_totals(full_dealer=False)
        self.feedbackLabel.setText("Your move: Hit or Stand")

        self.hitButton.setEnabled(True)
        self.standButton.setEnabled(True)


    def end_round(self):
        self.hitButton.setEnabled(False)
        self.standButton.setEnabled(False)
        self.recompute_card_size()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.recompute_card_size()

    def apply_theme(self):
        # Apply app-wide theme
        qss = self.dark_qss if self.is_dark else self.light_qss
        self.setStyleSheet(qss)

    def toggle_theme(self, checked: bool):
        self.is_dark = bool(checked)
        self.apply_theme()
        if hasattr(self, "themeAction"):
            self.themeAction.setChecked(self.is_dark)


# complete

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # macOS only fix for icons appearing
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())