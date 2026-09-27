#!/bin/bash

# Settings
DISCORD_APP="discord"
DISCORD_PROC="Discord" # actual process name of the discord binary
DISCORD_CLASS="discord"
SPECIAL_WS="discord"

discord_window_exists() {
    hyprctl clients | grep -q "class: $DISCORD_CLASS$"
}

# Start Discord if not running
if ! pgrep -x "$DISCORD_PROC" >/dev/null; then
    nohup "$DISCORD_APP" &>/dev/null &
fi

# Wait for the Discord window to appear (updater can take a while)
for _ in $(seq 1 60); do
    discord_window_exists && break
    sleep 0.5
done
discord_window_exists || exit 0

# Move Discord window to special workspace
hyprctl dispatch "hl.dsp.window.move({ window = \"class:^$DISCORD_CLASS\$\", workspace = \"special:$SPECIAL_WS\", follow = false })"

# Show special workspace overlayed on current workspace
hyprctl dispatch "hl.dsp.workspace.toggle_special(\"$SPECIAL_WS\")"
