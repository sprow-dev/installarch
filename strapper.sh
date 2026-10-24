pacstrap -K --noconfirm /mnt \
    # core
    amd-ucode base dosfstools efibootmgr grub linux linux-firmware nvidia nvidia-settings nvidia-utils os-prober \
    # desktop
    kde-applications plasma prismlauncher sddm wl-clipboard \
    # administration
    bluez bluez-utils nano networkmanager pacman-contrib sudo tailscale \
    # programming
    base-devel git uv \
    # utilities
    cowsay docker docker-compose fastfetch htop iotop kidskmark lolcat nvtop tree yt-dlp


genfstab -U /mnt >> /mnt/etc/fstab
mkdir -p /mnt/etc/default
cp cfgs/etc_default_grub /mnt/etc/default/grub
cp cfgs/etc_mkinitcpio.conf /mnt/etc/mkinitcpio.conf
cp cfgs/etc_locale.gen /mnt/etc/locale.gen
cp cfgs/etc_locale.conf /mnt/etc/locale.conf
mkdir -p /mnt/home/Sprow
cp cfgs/home_sprow_.bashrc /mnt/home/Sprow/.bashrc
cp cfgs/etc_pacman.d_hooks_cm.hook /mnt/etc/pacman.d/hooks/cm.hook
cp cfgs/etc_pacman.d_hooks_lp.hook /mnt/etc/pacman.d/hooks/lp.hook
cp cfgs/etc_pacman.conf /mnt/etc/pacman.conf
cp cfgs/etc_hosts /mnt/etc/hosts
cp cfgs/etc_sudoers /mnt/etc/sudoers
cp cfgs/etc_sddm.conf.d_kde_settings.conf /mnt/etc/sddm.conf.d/kde_settings.conf
echo "ArchLinux" > /mnt/etc/hostname
