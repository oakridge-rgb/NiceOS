#!/bin/bash
# NiceOS on Termux — apply the purple/blue reskin to a proot Debian.
#
# Run INSIDE the proot Debian (root by default):
#   bash <(curl -fsSL https://raw.githubusercontent.com/oakridge-rgb/NiceOS/main/termux/niceos-termux.sh)
#
# Then start the desktop:
#   export DISPLAY=:0 && startxfce4
#
# What applies here: Niceos GTK theme, Papirus-Dark icons, Noto Sans fonts,
# wallpaper, Mac-like panel/dock layout, welcome app, os-release identity.
# What does NOT apply on Android: Plymouth, GRUB theme, LightDM, Calamares.
set -e

[ "$(id -u)" = 0 ] || {
    echo "Run this as root inside 'proot-distro login debian --shared-tmp'." >&2
    exit 1
}
[ -n "${DISPLAY:-}" ] || DISPLAY=":0"

REPO_URL="https://github.com/oakridge-rgb/NiceOS"
SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
TMP="$(mktemp -d)"

echo "[1/4] Installing Debian packages..."
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    xfce4 xfce4-whiskermenu-plugin xfce4-terminal thunar mousepad \
    ristretto xarchiver galculator xfce4-screenshooter \
    x11-xserver-utils arc-theme papirus-icon-theme fonts-noto-core \
    dbus dbus-x11 git curl zenity >/dev/null

echo "[2/4] Fetching NiceOS reskin files..."
if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/xfce4-panel.xml" ]; then
    INC="$(dirname "$SCRIPT_DIR")/config/includes.chroot"
else
    git clone --depth 1 "$REPO_URL" "$TMP/NiceOS" >/dev/null 2>&1
    INC="$TMP/NiceOS/config/includes.chroot"
fi

echo "[3/4] Applying theme files..."
cp -a "$INC/usr/share/themes/Niceos" /usr/share/themes/
mkdir -p /usr/share/backgrounds/niceos /usr/share/niceos \
         /usr/share/icons/hicolor /usr/share/applications
cp -a "$INC/usr/share/backgrounds/niceos/." /usr/share/backgrounds/niceos/
cp -a "$INC/usr/share/icons/hicolor/." /usr/share/icons/hicolor/
cp -a "$INC/usr/share/niceos/." /usr/share/niceos/
cp -a "$INC"/usr/share/applications/niceos-*.desktop /usr/share/applications/
install -m 755 "$INC/usr/bin/niceos-welcome" /usr/bin/niceos-welcome
install -m 755 "$INC/usr/bin/niceos-apply-wallpaper" /usr/bin/niceos-apply-wallpaper

# Desktop defaults for the proot user (root) and any future users
cp -a "$INC/etc/skel/." /root/
cp -a "$INC/etc/skel/." /etc/skel/

# Termux-specific panel: no power plugin (no upower on Android) and no
# Firefox dock item (not installed here) — see termux/xfce4-panel.xml.
if [ -f "$SCRIPT_DIR/xfce4-panel.xml" ]; then
    cp "$SCRIPT_DIR/xfce4-panel.xml" \
       /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml
fi
# Software rendering on phones: disable compositing to stay smooth.
sed -i 's|name="use_compositing" type="bool" value="true"|name="use_compositing" type="bool" value="false"|' \
    /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml

echo "[4/4] Setting NiceOS identity..."
cat > /etc/os-release <<'EOF'
PRETTY_NAME="NiceOS 1.0 (Termux)"
NAME="NiceOS"
VERSION="1.0 (proot Debian)"
VERSION_ID="1.0"
ID=niceos
ID_LIKE=debian
HOME_URL="https://github.com/oakridge-rgb/NiceOS"
SUPPORT_URL="https://github.com/oakridge-rgb/NiceOS/issues"
EOF
printf 'NiceOS 1.0 (Termux) — Debian %s in proot.\n' \
    "$(cat /etc/debian_version 2>/dev/null || echo '?')" > /etc/motd
echo niceos > /etc/hostname 2>/dev/null || true

rm -rf "$TMP"

echo
echo "NiceOS applied. Start it with:"
echo "    export DISPLAY=:0 && startxfce4"
echo "(termux-x11 :0 must be running in Termux; see README.md, Termux section.)"
