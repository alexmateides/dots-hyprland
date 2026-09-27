-- --- LAPTOP (truepad) ---

-- Keep in sync with ~/.config/rofi/menus/display/display_menu.py
local internal = { output = "eDP-1", mode = "1920x1200@60", position = "0x0", scale = 1.333333 }

hl.monitor(internal)

-- --- EXTERNAL DISPLAY MENU (mirror / extend / ...) ---
local menuDir     = "~/.config/rofi/menus/display"
local displayMenu = "rofi -show display -modi display:" .. menuDir .. "/display_menu.py -theme " .. menuDir .. "/center.rasi"

hl.bind("SUPER + SHIFT + P", hl.dsp.exec_cmd(displayMenu))

-- Applying a mode re-adds outputs, don't pop the menu up again right after
local function recently_applied()
    local f = io.open((os.getenv("XDG_RUNTIME_DIR") or "/tmp") .. "/display-menu.stamp")
    if not f then return false end
    local t = tonumber(f:read("*l"))
    f:close()
    return t ~= nil and os.time() - t < 5
end

local function is_connected(name)
    for card = 0, 3 do
        local f = io.open("/sys/class/drm/card" .. card .. "-" .. name .. "/status")
        if f then
            local status = f:read("*l")
            f:close()
            return status == "connected"
        end
    end
    return false
end

hl.on("monitor.added", function(m)
    if m.name == internal.output or recently_applied() then return end
    hl.exec_cmd("pidof rofi >/dev/null || " .. displayMenu)
end)

-- Unplugged: turn the panel back on and forget the mode chosen for that output
hl.on("monitor.removed", function(m)
    if m.name == internal.output or is_connected(m.name) then return end
    hl.monitor({ output = m.name, mode = "preferred", position = "auto", scale = 1.333333, disabled = false, mirror = "" })
    hl.monitor({ output = internal.output, mode = internal.mode, position = internal.position, scale = internal.scale, disabled = false, mirror = "" })
end)
