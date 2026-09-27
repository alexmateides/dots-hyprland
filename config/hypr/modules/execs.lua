-- --- EXECS ---
-- See https://wiki.hypr.land/Configuring/Basics/Autostart/
hl.on("hyprland.start", function()
    -- Import the Wayland env into systemd first, so the user services below can reach the compositor.
    -- reset-failed: if a previous Hyprland exited, these crash-loop into start-limit-hit and a plain start is refused
    hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP HYPRLAND_INSTANCE_SIGNATURE && systemctl --user reset-failed hyprpolkitagent vicinae hypridle; systemctl --user start hyprpolkitagent vicinae hypridle")

    -- Hand the login password from pam_kwallet5 (etc/pam.d/greetd) to KWallet so it unlocks without a prompt
    hl.exec_cmd("/usr/lib/pam_kwallet_init")

    hl.exec_cmd("/usr/bin/dunst")
    hl.exec_cmd("waybar") -- topbar
    hl.exec_cmd("awww-daemon") -- wallpaper (swww was renamed to awww)
    -- Wait for the daemon socket before setting the image
    hl.exec_cmd("sh -c 'until awww query >/dev/null 2>&1; do sleep 0.1; done; awww img ~/.config/assets/backgrounds/cat_leaves.png --transition-fps 255 --transition-type outer --transition-duration 0.8'")
    hl.exec_cmd("wl-paste --type text --watch cliphist store") -- clipboard
    hl.exec_cmd("wl-paste --type image --watch cliphist store")
    -- hl.exec_cmd('rm "$HOME/.cache/cliphist/db"') -- it'll delete history at every restart

    -- --- RGB --- (desktop only)
    local f = io.open("/etc/hostname")
    local host = f and f:read("*l") or ""
    if f then f:close() end
    if host == "truepeak-pc" then
        hl.exec_cmd("openrgb -c FF00FF")
    end
end)
