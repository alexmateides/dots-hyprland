hl.on("hyprland.start", function()
    hl.exec_cmd("regreet --style /etc/greetd/config.css; hyprctl dispatch 'hl.dsp.exit()'")
end)

hl.config({
    misc = {
        disable_hyprland_logo    = true,
        disable_splash_rendering = true,
    },

    input = {
        numlock_by_default = true,
    },

    debug = {
        suppress_errors = true,
    },
})
