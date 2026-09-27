-- --- ENVIRONMENT VARIABLES ---
-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Environment-variables/
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")

-- QT
hl.env("QT_QPA_PLATFORM", "wayland")
-- "kde" (plasma-integration) reads ~/.config/kdeglobals, so KDE apps like Dolphin get the full
-- Rosé Pine palette; qt6ct left KColorScheme-driven views on light defaults (white alternating rows)
hl.env("QT_QPA_PLATFORMTHEME", "kde")
hl.env("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
hl.env("QT_STYLE_OVERRIDE", "kvantum")

-- Toolkit Backend Variables
hl.env("GDK_BACKEND", "wayland")
hl.env("SDL_VIDEODRIVER", "wayland")
hl.env("CLUTTER_BACKEND", "wayland")

-- XDG Specifications
hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_TYPE", "wayland")
hl.env("XDG_SESSION_DESKTOP", "Hyprland")
hl.env("XDG_MENU_PREFIX", "arch-")

-- Electron (only honoured by electron < 38; newer apps use ~/.config/electron-flags.conf)
hl.env("ELECTRON_OZONE_PLATFORM_HINT", "wayland")

-- Dark theme (runs on every config load, like the old `exec =`)
hl.exec_cmd('gsettings set org.gnome.desktop.interface gtk-theme "Adwaita-dark"')
hl.exec_cmd('gsettings set org.gnome.desktop.interface color-scheme "prefer-dark"')

-- Default editor (for apps launched outside a shell)
hl.env("EDITOR", "nano")
hl.env("VISUAL", "nano")

-- Hyprshot
hl.env("HYPRSHOT_DIR", os.getenv("HOME") .. "/Pictures/screenshots")
