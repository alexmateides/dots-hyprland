-- --- MONITOR CONFIG ---
-- See https://wiki.hypr.land/Configuring/Basics/Monitors/
-- Per-machine setup lives in hosts/<hostname>.lua

-- Fallback for unknown / hotplugged outputs
hl.monitor({ output = "",         mode = "preferred",        position = "auto",     scale = 1.333333 })

local f = io.open("/etc/hostname")
local host = f and f:read("*l") or ""
if f then f:close() end

local ok, err = pcall(require, "hosts." .. host)
if not ok then
    print("monitors: no host config for '" .. host .. "': " .. tostring(err))
end
