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
sudo mkdir -p /boot/grub/themes
sudo cp -r ./CyberGRUB-2077 /boot/grub/themes/CyberGRUB-2077
```

> Modify config

```bash
sudo grub-mkconfig -o /boot/grub/grub.cfg
```


