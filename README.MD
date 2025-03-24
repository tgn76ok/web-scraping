sudo apt install flatpak -y
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

flatpak install flathub com.github.micahflee.torbrowser-launcher -y
flatpak list
flatpak run org.torproject.torbrowser-launcher