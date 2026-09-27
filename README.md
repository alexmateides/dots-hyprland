### My Hyprland dots

> Dots for my Hyprland configuration

---

### Specific issues

#### 1. Dolphin default app not persistent

> https://github.com/prasanthrangan/hyprdots/issues/1406

#### 2. Pycharm scaling

> https://blog.jetbrains.com/platform/2024/07/wayland-support-preview-in-2024-2/

#### 3. Grub

```bash
cd ~
git clone https://github.com/adnksharp/CyberGRUB-2077
cd CyberGRUB-2077
sudo fish install.fish
```

> Modify config

```bash
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

#### 4. KDE Wallet (Dolphin encrypted drives: "error 9 - read error")

> Dolphin stores LUKS passphrases in KWallet; if the wallet can't be unlocked, unlocking the drive fails even with the right passphrase.
> `etc/pam.d/greetd` + `pam_kwallet_init` in `execs.lua` unlock the wallet at login, but the wallet has to be created once by hand.

```bash
# move any existing wallet out of the way
mkdir -p ~/kwallet-old && mv ~/.local/share/kwalletd/kdewallet.* ~/kwallet-old/
kwalletmanager
```

> In kwalletmanager create a new wallet:
> - name: `kdewallet`
> - type: classic Blowfish (not GPG)
> - password: same as the login password

> Log out and back in through greetd. If the login password changes, change the wallet password too.

### Useful commands

#### Packages

```bash
yay -S --needed $(cat packages/*.txt)
```


