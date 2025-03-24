sudo apt install flatpak -y
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

flatpak install flathub com.github.micahflee.torbrowser-launcher -y
flatpak list
flatpak run org.torproject.torbrowser-launcher

ControlPort 9051
HashedControlPassword 16:937D9C2BBA279EAB60306989D9DF59D646FE0F10E986C19C6D1707CEAA
