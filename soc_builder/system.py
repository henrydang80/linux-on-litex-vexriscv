#!/usr/bin/env python3
import os
import sys
import math
import struct
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.boards.platforms import basys3

class System(Module):
    def __init__(self, platform):
        serial     = platform.request("serial")
        clk100     = platform.request("clk")
        spi0       = platform.request("spi")
        spi_slave0 = platform.request("spi_slave")

        # POR implementation
        self.reset = Signal()
        self.clock_domains.cd_por = ClockDomain()
        self.reset_delay = Signal(12, reset=4095)

        self.comb += [
            self.cd_por.clk.eq(clk100),
        ]

        self.sync.por += [
            self.reset.eq(self.reset_delay != 0)
        ]

        self.sync.por += [
            If(self.reset_delay != 0,
                self.reset_delay.eq(self.reset_delay - 1)
            )
        ]

        # Accel sim core
        self.specials += Instance("accel_sim_core",
            i_clk                 = clk100,
            i_rst                 = self.reset,
            i_serial_rx           = serial.rx,
            o_serial_tx           = serial.tx,

            # SPI master
            o_spi0_sclk           = spi0.sclk,
            i_spi0_miso           = spi0.miso,
            o_spi0_mosi           = spi0.mosi,
            o_spi0_csn            = spi0.csn,
           #i_spi0_irq            = spi0.irq,
	
            # SPI slave, accel
            i_spi_slave0_sck      = spi_slave0.sck,
           io_spi_slave0_miso     = spi_slave0.miso,
            i_spi_slave0_mosi     = spi_slave0.mosi,
            i_spi_slave0_csn      = spi_slave0.csn,
            o_spi_slave0_int1     = spi_slave0.int1,
           #o_spi_slave0_int2     = spi_slave0.int2,

            # Debug LEDs
            o_spi_slave0_led0     = spi_slave0.led0,
            o_spi_slave0_led1     = spi_slave0.led1,
            o_spi_slave0_led2     = spi_slave0.led2,
            o_spi_slave0_led3     = spi_slave0.led3,
            o_spi_slave0_led4     = spi_slave0.led4,
            o_spi_slave0_led5     = spi_slave0.led5,
            o_spi_slave0_led6     = spi_slave0.led6,
	
            # Accel uart
            #i_spi_slave0_tx      = spi_slave0.tx,
            #i_spi_slave0_rx      = spi_slave0.rx,
        )

        platform.add_source(os.path.join("build/accel_sim/gateware", "accel_sim_core.v"))
        platform.add_source(os.path.join("build/accel_sim/gateware", "accel_sim_core.init"))
        platform.add_source(os.path.join("build/accel_sim/gateware", "mem_1.init"))
        platform.add_source(os.path.join("build/accel_sim/gateware", "mem_2.init"))
        platform.add_source(os.path.join("../litex/litex/soc/cores/cpu/vexriscv/verilog", "VexRiscv_Min.v"))
        platform.add_source(os.path.join("../periphs/verilog/spi", "spi_defines.v"))
        platform.add_source(os.path.join("../periphs/verilog/spi", "spi_clgen.v"))
        platform.add_source(os.path.join("../periphs/verilog/spi", "spi_shift.v"))
        platform.add_source(os.path.join("../periphs/verilog/spi", "spi_top.v"))
        platform.add_source(os.path.join("../periphs/verilog/spi", "timescale.v"))

def main():
    description = "LiteX-VexRiscv SoC Builder\n\n"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--build", action="store_true", help="build bitstream")
    parser.add_argument("--load", action="store_true", help="load bitstream (to SRAM)")
    parser.add_argument("--flash", action="store_true", help="flash bitstream/images (to SPI Flash)")
    args = parser.parse_args()

    if args.build:
        platform = basys3.Platform()
        dut = System(platform)
        platform.build(dut, build_dir="build/system/gateware")

    if args.load:
        from litex.build.xilinx import VivadoProgrammer
        prog = VivadoProgrammer()
        prog.load_bitstream("build/system/gateware/top.bit")

    if args.flash:
        from litex.build.openocd import OpenOCD
        prog = OpenOCD("prog/openocd_xilinx.cfg",
            flash_proxy_basename="prog/bscan_spi_xc7a35t.bit")
        prog.set_flash_proxy_dir(".")
        prog.flash(0, "build/system/gateware/top.bin")

if __name__ == "__main__":
    main()       