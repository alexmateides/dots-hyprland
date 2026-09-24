#!/bin/bash

# Settings
DISCORD_APP="discord"
SPECIAL_WS="discord"

# Start Discord if not running
if ! pgrep -x "$DISCORD_APP" >/dev/null; then
    nohup $DISCORD_APP &>/dev/null &
    # Sleep to allow Discord to actually launch (tweak as needed)
    sleep 3
fi

# Move Discord window to special workspace
# Requires hyprctl (installed with Hyprland)
DISCORD_WIN=$(hyprctl clients -j | jq -r '.[] | select(.class=="discord") | .address')
if [ -z "$DISCORD_WIN" ]; then
    exit 0
fi

hyprctl dispatch "hl.dsp.window.move({ window = \"address:$DISCORD_WIN\", workspace = \"special:$SPECIAL_WS\", follow = false })"

# Show special workspace overlayed on current workspace
hyprctl dispatch "hl.dsp.workspace.toggle_special(\"$SPECIAL_WS\")"
