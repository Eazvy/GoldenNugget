"""Shared project credits for the About dialog and idle support panel."""
from pathlib import Path
from PySide6.QtCore import QT_TRANSLATE_NOOP

CREDITS = [
    (QT_TRANSLATE_NOOP("SupportPanel", "Owner / Main Developer"), "awesomenull", "https://github.com/awesomenull-dev"),
    (QT_TRANSLATE_NOOP("SupportPanel", "Co-Developer"), "Windows11Aero", "https://github.com/Wind0ws11Aero"),
    (QT_TRANSLATE_NOOP("SupportPanel", "Co-Developer"), "kik4311", "https://github.com/kik4311"),
    (QT_TRANSLATE_NOOP("SupportPanel", "Nugget Creator"), "leminlimez", "https://github.com/leminlimez"),
    (QT_TRANSLATE_NOOP("SupportPanel", "Icon Artwork"), "mekabrine", "https://discord.com/users/1196529222617923660"),
    (QT_TRANSLATE_NOOP("SupportPanel", "PosterRestore Team"), "PosterRestore Discord", "https://discord.com/invite/gWtzTVhMvh"),
    (QT_TRANSLATE_NOOP("SupportPanel", "PosterBoard Help"), "dootskyre, Middo, dulark, forcequitOS, pengubow", "https://x.com/dootskyre"),
    (QT_TRANSLATE_NOOP("SupportPanel", "Wallpaper Website"), "SerStars", "https://cowabun.ga/wallpapers"),
    (QT_TRANSLATE_NOOP("SupportPanel", "Global Flags"), "disfordottie", "https://x.com/disfordottie"),
    (QT_TRANSLATE_NOOP("SupportPanel", "Springboard/Internal"), "iTechExpert", "https://x.com/iTechExpert21"),
    (QT_TRANSLATE_NOOP("SupportPanel", "Quiet Daemon"), "Mikasa-san", "https://github.com/Mikasa-san/QuietDaemon"),
    (QT_TRANSLATE_NOOP("SupportPanel", "pymobiledevice3"), "doronz88", "https://github.com/doronz88/pymobiledevice3"),
    (QT_TRANSLATE_NOOP("SupportPanel", "PySide6"), "Qt Company", "https://doc.qt.io/qtforpython-6/"),
    (QT_TRANSLATE_NOOP("SupportPanel", "AAR Handling"), "Snoolie", "https://github.com/0xilis/python-aar-stuff"),
    (QT_TRANSLATE_NOOP("SupportPanel", "AI Eligibility"), "f1shy-dev", "https://github.com/f1shy-dev"),
    (QT_TRANSLATE_NOOP("SupportPanel", "PosterBoard Icons"), "JJTech", "https://github.com/JJTech0130"),
    (QT_TRANSLATE_NOOP("SupportPanel", "AirLift"), "0xjohnnydev", "https://github.com/0xjohnnydev/airlift"),
    (QT_TRANSLATE_NOOP("SupportPanel", "Translations"), QT_TRANSLATE_NOOP("SupportPanel", "GoldenNugget translation contributors"), "https://github.com/GoldenNugget-Team/gNugget-i18n"),
    (QT_TRANSLATE_NOOP("SupportPanel", "Legacy Translations"), QT_TRANSLATE_NOOP("SupportPanel", "Nugget translation contributors"), "https://poeditor.com/join/project/UTqpVSE2UD"),
]

CREDIT_AVATARS = {
    "https://doc.qt.io/qtforpython-6/":
        str(Path(__file__).resolve().parents[1] / "qt" / "credits" / "pyside6.png"),
    "https://x.com/disfordottie":
        str(Path(__file__).resolve().parents[1] / "qt" / "credits" / "disfordottie.jpg"),
    "https://x.com/iTechExpert21":
        str(Path(__file__).resolve().parents[1] / "qt" / "credits" / "itech-expert.jpg"),
    "https://discord.com/users/1196529222617923660":
        str(Path(__file__).resolve().parents[1] / "qt" / "credits" / "mekabrine.webp"),
}

CREDIT_AVATAR_SOURCES = {
    "https://cowabun.ga/wallpapers": "https://github.com/serstars",
}
