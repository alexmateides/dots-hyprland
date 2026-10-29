### My Hyprland dots

> Dots for my Hyprland configuration

---

### Specific issues

#### 1. Dolphin default app not persistent

> https://github.com/prasanthrangan/hyprdots/issues/1406

#### 2. Pycharm scaling

> https://blog.jetbrains.com/platform/2024/07/wayland-support-preview-in-2024-2/

#### 3. Grub

> Theme: [CyberGRUB-2077](https://github.com/adnksharp/CyberGRUB-2077) by adnksharp (Unlicense), copied into `grub/` (see `grub/README.md`).

```bash
sudo scripts/setup_grub_theme.sh   # copies it to /boot/grub/themes, sets GRUB_THEME, runs grub-mkconfig
```

> OS icons: `etc/grub.d/15_uki` (copied by `apply.sh`) writes the UKIs as entries with `--class arch ...`; grub's built-in `uki` command has no classes, so the theme showed no icons. Re-run `grub-mkconfig` after `apply.sh`.

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

#### 5. Suspend-then-hibernate (laptop)

> s2idle for 3h on battery, then hibernate to a btrfs swapfile (`etc/systemd/sleep.conf.d/hibernate.conf`). One-time setup:

```bash
sudo scripts/setup_hibernate.sh   # @swap subvolume + 32G swapfile, resume hook, resume_offset, rebuilds UKI
reboot
systemctl hibernate               # test
```

#### 6. Plymouth (CyberGRUB-2077 boot splash / LUKS prompt)

> Theme in `plymouth/cybergrub-2077`, artwork from the grub theme in `grub/`. Text is pre-rendered, re-run `render_text.sh` in the theme dir after editing it.

```bash
sudo scripts/setup_plymouth.sh    # plymouth, theme, hook before encrypt, quiet splash, drops the Arch UKI splash, rebuilds UKI
```

> Boot -> login handover: `etc/systemd/system/plymouth-quit.service.d/retain-splash.conf` keeps the last splash frame ("START DESKTOP") on screen until the greeter's Hyprland takes the display.

### Useful commands

#### Packages

```bash
yay -S --needed $(cat packages/*.txt)
```


