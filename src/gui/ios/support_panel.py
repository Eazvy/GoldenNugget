from PySide6.QtCore import Qt, QSize, QUrl, QRectF, QCoreApplication
from PySide6.QtGui import QDesktopServices, QPixmap, QPainter, QPainterPath, QIcon, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QToolButton, QSizePolicy,
)

from src.gui.credits import CREDITS
from src.gui.widgets import (
    IOSCard, IOSCollapsibleSection,
)
from src.gui.theme import ColorThemeManager, theme_pixmap, t


def _tr(text):
    return QCoreApplication.translate("SupportPanel", text)


class SupportPanel(IOSCard):
    def __init__(self, parent=None, links=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(18)
        self.title = QLabel(_tr('Developers / Contributors'))
        self.title.setObjectName('supportTitle')
        layout.addWidget(self.title)
        if links is None:
            links = CommunityLinks(self)
            layout.addWidget(links)
        self.discord = links.discord
        self.github = links.github
        team = QHBoxLayout()
        team.setSpacing(12)
        portraits = (
            ":/credits/awesomenull.png",
            ":/credits/windows11aero.png",
            ":/credits/kik4311.png",
            ":/credits/LeminLimez.png",
        )
        for (role, name, url), portrait in zip(CREDITS[:len(portraits)], portraits):
            team.addWidget(self._profile(role, name, url, portrait), 1)
        layout.addLayout(team)
        credits = IOSCollapsibleSection(_tr('Contributors && acknowledgements'), expanded=False)
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(16)
        for index, (role, name, url) in enumerate(CREDITS[len(portraits):]):
            grid.addWidget(self._credit(role, name, url), index // 2, index % 2)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        credits.body_layout.addLayout(grid)
        layout.addWidget(credits)
        self._retheme()

    def _profile(self, role, name, url, portrait):
        tile = QWidget()
        tile.setObjectName('supportProfile')
        tile.setMinimumHeight(188)
        column = QVBoxLayout(tile)
        column.setContentsMargins(16, 18, 16, 16)
        column.setSpacing(9)
        avatar = QToolButton()
        avatar.setFixedSize(92, 92)
        avatar.setIconSize(QSize(88, 88))
        avatar.setIcon(QIcon(self._portrait(portrait)))
        avatar.setObjectName('supportAvatar')
        avatar.setToolTip(f'{name} · {role}')
        avatar.setAccessibleName(f'{name} · {role}')
        avatar.setCursor(Qt.PointingHandCursor)
        avatar.clicked.connect(lambda _, link=url: QDesktopServices.openUrl(QUrl(link)))
        column.addWidget(avatar, 0, Qt.AlignHCenter)
        name_button = QPushButton(name)
        name_button.setObjectName('supportName')
        name_button.setCursor(Qt.PointingHandCursor)
        name_button.clicked.connect(lambda _, link=url: QDesktopServices.openUrl(QUrl(link)))
        column.addWidget(name_button)
        caption = QLabel(_tr(role))
        caption.setObjectName('supportMuted')
        caption.setWordWrap(True)
        caption.setAlignment(Qt.AlignCenter)
        column.addWidget(caption)
        column.addStretch()
        return tile

    @staticmethod
    def _credit(role, name, url):
        entry = QWidget()
        column = QVBoxLayout(entry)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(4)
        label = QLabel(_tr(role))
        label.setObjectName('supportMuted')
        column.addWidget(label)
        link = QLabel(f'<a href="{url}">{_tr(name)}</a>')
        link.setObjectName('supportCredit')
        link.setWordWrap(True)
        link.setOpenExternalLinks(True)
        column.addWidget(link)
        return entry


    @staticmethod
    def _portrait(resource):
        source = QPixmap(resource).scaled(
            176, 176, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        image = QPixmap(176, 176)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        mask = QPainterPath()
        mask.addEllipse(QRectF(0, 0, 176, 176))
        painter.setClipPath(mask)
        painter.drawPixmap((176 - source.width()) // 2, (176 - source.height()) // 2, source)
        painter.end()
        image.setDevicePixelRatio(2)
        return image

    def _retheme(self):
        super()._retheme()
        self.setStyleSheet(self.styleSheet() + t("support_panel"))


class CommunityLinks(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)
        self.setMaximumWidth(340)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        self._counts = []
        for title in ('Tweaks', 'Daemons'):
            card = QWidget(self)
            card.setObjectName('selectionCount')
            card.setFixedHeight(80)
            column = QVBoxLayout(card)
            column.setContentsMargins(12, 10, 12, 10)
            column.setSpacing(4)
            value = QLabel('0', card)
            value.setAlignment(Qt.AlignCenter)
            caption = QLabel(_tr(title + ' enabled'), card)
            caption.setAlignment(Qt.AlignCenter)
            column.addWidget(value)
            column.addWidget(caption)
            layout.addWidget(card, 0, len(self._counts))
            self._counts.append((title.lower(), card, value, caption))
        self._links = []
        for title, icon, url in (
            ('Golden Nugget Support', ':/icon/discord.svg', 'https://discord.gg/F7ssrHjdgK'),
            ('Source Code', ':/icon/github.svg', 'https://github.com/GoldenNugget-Team/GoldenNugget'),
        ):
            button = QPushButton(self)
            button.setObjectName('communityLink')
            button.setFixedHeight(80)
            button.setCursor(Qt.PointingHandCursor)
            button.setAccessibleName(_tr(title))
            button.clicked.connect(lambda checked=False, link=url: QDesktopServices.openUrl(QUrl(link)))
            column = QVBoxLayout(button)
            column.setContentsMargins(10, 9, 10, 9)
            column.setSpacing(3)
            badge = QLabel(button)
            badge.setFixedSize(26, 26)
            badge.setAlignment(Qt.AlignCenter)
            top = QGridLayout()
            top.setContentsMargins(0, 0, 0, 0)
            top.setColumnMinimumWidth(0, 16)
            top.setColumnMinimumWidth(2, 16)
            top.setColumnStretch(1, 1)
            top.addWidget(badge, 0, 1, Qt.AlignCenter)
            arrow = QLabel('↗', button)
            arrow.setFixedSize(16, 20)
            arrow.setAlignment(Qt.AlignCenter)
            top.addWidget(arrow, 0, 2, Qt.AlignTop | Qt.AlignRight)
            column.addLayout(top)
            heading = QLabel(_tr(title), button)
            heading.setAlignment(Qt.AlignCenter)
            heading.setWordWrap(True)
            heading.setFixedHeight(30)
            column.addWidget(heading)
            for label in (badge, heading, arrow):
                label.setAttribute(Qt.WA_TransparentForMouseEvents)
            layout.addWidget(button, 1, len(self._links))
            self._links.append((button, icon, badge, heading, arrow))
        self.discord = self._links[0][0]
        self.github = self._links[1][0]
        self._retheme()

    def set_counts(self, counts, totals):
        for key, card, value, caption in self._counts:
            value.setText(str(counts.get(key, 0)))
            card.setToolTip(_tr('{0} available').format(totals.get(key, 0)))

    def _retheme(self):
        c = ColorThemeManager.instance().colors
        for key, card, value, caption in self._counts:
            card.setStyleSheet(f'QWidget#selectionCount {{ background:{c.bg_secondary}; border:1px solid {c.border}; border-radius:16px; }}')
            value.setStyleSheet(f'color:{c.accent}; background:transparent; font-size:26px; font-weight:700;')
            caption.setStyleSheet(f'color:{c.text_secondary}; background:transparent; font-size:12px;')
        dark = QColor(c.bg_secondary).lightnessF() < 0.5
        for button, icon, badge, heading, arrow in self._links:
            color = '#5865F2' if 'discord' in icon else '#FFFFFF' if dark else '#24292F'
            badge.setPixmap(theme_pixmap(icon, color, 24, self.devicePixelRatioF()))
            badge.setStyleSheet('background:transparent;')
            arrow.setStyleSheet(f'background:transparent; color:{c.text_secondary}; font-size:15px;')
            heading.setStyleSheet(f'background:transparent; color:{c.text_primary}; font-size:12px; font-weight:500;')
            button.setStyleSheet(f"""
                QPushButton#communityLink {{ background:{c.bg_secondary};
                    border:1px solid {c.border}; border-radius:16px; padding:0; }}
                QPushButton#communityLink:hover {{ background:{c.surface_hover}; }}
                QPushButton#communityLink:pressed {{ border-color:{c.text_secondary}; }}
            """)
