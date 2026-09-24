-----------------------
----- PERMISSIONS -----
-----------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Permissions/
-- Please note permission changes here require a Hyprland restart and are not applied on-the-fly
-- for security reasons

-- hl.config({
--     ecosystem = {
--         enforce_permissions = true,
--     },
-- })

-- hl.permission("/usr/(bin|local/bin)/grim", "screencopy", "allow")
-- hl.permission("/usr/(lib|libexec|lib64)/xdg-desktop-portal-hyprland", "screencopy", "allow")
-- hl.permission("/usr/(bin|local/bin)/hyprpm", "plugin", "allow")


-----------------------
---- LOOK AND FEEL ----
-----------------------

-- Refer to https://wiki.hypr.land/Configuring/Basics/Variables/
hl.config({
    general = {
        gaps_in  = 5,
        gaps_out = 5,

        border_size = 1,

        col = {
            active_border   = { colors = { "rgba(33ccffee)", "rgba(00ff99ee)" }, angle = 45 },
            inactive_border = "rgba(595959aa)",
        },

        -- Set to true enable resizing windows by clicking and dragging on borders and gaps
        resize_on_border = false,

        -- Please see https://wiki.hypr.land/Configuring/Advanced-and-Cool/Tearing/ before you turn this on
        allow_tearing = false,

        layout = "dwindle",
    },

    decoration = {
        rounding = 7,

        active_opacity   = 1.0,
        inactive_opacity = 0.9,

        blur = {
            enabled           = true,
            xray              = false,
            special           = false,
            ignore_opacity    = true, -- Allows opacity blurring
            new_optimizations = true,
            popups            = true,
            input_methods     = true,
        },

        shadow = {
            enabled = true,
            range   = 4,
            color   = "rgba(1a1a1aee)",
        },
    },

    animations = {
        enabled = true,
    },
})

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Animations/

-- Animation curves
hl.curve("specialWorkSwitch", { type = "bezier", points = { {0.05, 0.7}, {0.1, 1}    } })
hl.curve("emphasizedAccel",   { type = "bezier", points = { {0.3, 0},    {0.8, 0.15} } })
hl.curve("emphasizedDecel",   { type = "bezier", points = { {0.05, 0.7}, {0.1, 1}    } })
hl.curve("standard",          { type = "bezier", points = { {0.2, 0},    {0, 1}      } })

-- Animation configs
hl.animation({ leaf = "layersIn",   enabled = true, speed = 5, bezier = "emphasizedDecel", style = "slide" })
hl.animation({ leaf = "layersOut",  enabled = true, speed = 4, bezier = "emphasizedAccel", style = "slide" })
hl.animation({ leaf = "fadeLayers", enabled = true, speed = 5, bezier = "standard" })

hl.animation({ leaf = "windowsIn",   enabled = true, speed = 5, bezier = "emphasizedDecel" })
hl.animation({ leaf = "windowsOut",  enabled = true, speed = 3, bezier = "emphasizedAccel" })
hl.animation({ leaf = "windowsMove", enabled = true, speed = 6, bezier = "standard" })
hl.animation({ leaf = "workspaces",  enabled = true, speed = 5, bezier = "standard" })

hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 4, bezier = "specialWorkSwitch", style = "slidefadevert 15%" })

hl.animation({ leaf = "fade",    enabled = true, speed = 6, bezier = "standard" })
hl.animation({ leaf = "fadeDim", enabled = true, speed = 6, bezier = "standard" })
hl.animation({ leaf = "border",  enabled = true, speed = 6, bezier = "standard" })
