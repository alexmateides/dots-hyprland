-- --- DESKTOP (truepeak-pc) MONITORS ---

hl.monitor({ output = "DP-1",     mode = "2560x1440@144",    position = "1536x0",   scale = 1.25 })
hl.monitor({ output = "DP-4",     mode = "2560x1440@144",    position = "3584x144", scale = 1.25 })
hl.monitor({ output = "HDMI-A-1", mode = "1920x1080@100",    position = "0x144",    scale = 1.25 })

hl.workspace_rule({ workspace = "1", monitor = "DP-1" })
hl.workspace_rule({ workspace = "2", monitor = "DP-4" })
hl.workspace_rule({ workspace = "3", monitor = "HDMI-A-1" })
