// This is the source code of AyuGram for Desktop.
//
// We do not and cannot prevent the use of our code,
// but be respectful and credit the original author.
//
// Copyright @Radolyn, 2026
#pragma once

#define ICON(name, value) const auto name##_ICON = QStringLiteral(value)

namespace AyuAssets {

ICON(DEFAULT, "default");
ICON(LIGHT, "light");
ICON(NEON, "neon");
ICON(GOLD, "gold");
ICON(PINK, "pink");
ICON(OCEAN, "ocean");
ICON(PEAKS, "peaks");
ICON(GHOST, "ghost");
ICON(GHOSTNIGHT, "ghostnight");
ICON(MOON, "moon");
ICON(AURORA, "aurora");
ICON(SLEEPY, "sleepy");
ICON(EYE, "eye");
ICON(SPARK, "spark");
ICON(SUNSET, "sunset");
ICON(PLANET, "planet");
ICON(BUBBLE, "bubble");
ICON(SHADOW, "shadow");
ICON(MASK, "mask");
ICON(RING, "ring");

void loadAppIco();
QString appIcoPath();

QImage loadPreview(const QString& name);

QString currentAppLogoName();
QImage currentAppLogo();
QImage currentAppLogoPad();

}
