-- --- EXECS ---
-- See https://wiki.hypr.land/Configuring/Basics/Autostart/
hl.on("hyprland.start", function()
    -- Import the Wayland env into systemd first, so the user services below can reach the compositor
    hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP && systemctl --user start hyprpolkitagent vicinae hypridle")

    hl.exec_cmd("/usr/bin/dunst")
    hl.exec_cmd("waybar") -- topbar
    hl.exec_cmd("awww-daemon") -- wallpaper (swww was renamed to awww)
    -- Wait for the daemon socket before setting the image
    hl.exec_cmd("sh -c 'until awww query >/dev/null 2>&1; do sleep 0.1; done; awww img ~/.config/assets/backgrounds/cat_leaves.png --transition-fps 255 --transition-type outer --transition-duration 0.8'")
    hl.exec_cmd("wl-paste --type text --watch cliphist store") -- clipboard
    hl.exec_cmd("wl-paste --type image --watch cliphist store")
    -- hl.exec_cmd('rm "$HOME/.cache/cliphist/db"') -- it'll delete history at every restart

    -- --- RGB ---
    hl.exec_cmd("openrgb -c FF00FF")
end)
