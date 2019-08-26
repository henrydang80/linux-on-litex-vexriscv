
soc_config = {

    # Platform name ------------------------------------------------------------
    "platform_name": "accel_sim_release", # Platform name
    "soc_ident":     "accel_sim_release", # SoC indentify

    # General ------------------------------------------------------------------
    "cpu":         "vexriscv",    # Type of CPU used for init/calib (vexriscv)
    "cpu_variant": "minimal",     # CPU variant
    "speedgrade":  -1,            # FPGA speedgrade
    "mbx_sender":   "no",         # Integrated mailbox sender
    "mbx_receiver": "no",         # Integrated mailbox receiver

    # Frequency ----------------------------------------------------------------
    "input_clk_freq":   100e6,    # Input clock frequency
    "sys_clk_freq":     100e6,    # System clock frequency
    "iodelay_clk_freq": 200e6,    # IODELAYs reference clock frequency

    # Memory -------------------------------------------------------------------
    "rom_size":         64*1014,  # Integrated rom size
    "sram_size":        6*1024,   # Integrated sram size
}
