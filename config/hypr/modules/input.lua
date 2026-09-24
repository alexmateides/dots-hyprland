-- See https://wiki.hypr.land/Configuring/Basics/Variables/#input
hl.config({
    input = {
        kb_layout  = "cz",
        kb_variant = "coder",
        -- follow_mouse = 1,
        sensitivity        = 0,
        force_no_accel     = true,
        accel_profile      = "flat",
        numlock_by_default = true,

        touchpad = {
            natural_scroll = true,
        },
    },
})

-- Gestures, see https://wiki.hypr.land/Configuring/Basics/Gestures/
-- hl.gesture({
--     fingers   = 3,
--     direction = "horizontal",
--     action    = "workspace",
-- })
