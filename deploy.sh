ln -sf /usr/share/zoneinfo/America/Denver /etc/localtime
hwclock --systohc

locale-gen

echo "Please enter your new root password:"
passwd

useradd -m -G wheel,docker -s /bin/bash Sprow
echo "Please enter your new password for 'Sprow':"
passwd Sprow

grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=GRUB --removable
grub-mkconfig -o /boot/grub/grub.cfg

systemctl enable NetworkManager
systemctl enable bluetooth
systemctl enable docker
systemctl enable sddm

mkinitcpio -P

script -e -c 'su - Sprow -c "cd ~ && git clone https://aur.archlinux.org/yay.git ~/yay && cd ~/yay && makepkg -si --noconfirm"' /dev/null
script -e -c 'su - Sprow -c "yay -S --noconfirm --answerclean None --answerdiff None google-chrome kwin-effects-better-blur-dx-git localepurge"' /dev/null
