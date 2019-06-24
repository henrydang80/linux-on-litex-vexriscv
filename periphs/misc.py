import os

from migen import *
from litex.soc.interconnect import wishbone
from litex.soc.integration.soc_core import mem_decoder

from litex.soc.interconnect.csr import *
from litex.soc.interconnect.csr_eventmanager import *

# GPIO interrupt
class GpioISR(Module, AutoCSR):
    def __init__(self, pad, rissing_edge_detect = False):
        # Add int to module
        self.submodules.ev = EventManager()

        if rissing_edge_detect:
            self.ev.gpio_rising_int = EventSourcePulse()
            self.ev.finalize()
            self.comb += self.ev.gpio_rising_int.trigger.eq(pad)
        else:
            self.ev.gpio_falling_int = EventSourceProcess()
            self.ev.finalize()
            self.comb += self.ev.gpio_falling_int.trigger.eq(pad)

# Simple Adder8 module
class Adder8(Module, AutoCSR):
    def __init__(self):
        self.op1 = CSRStorage(8)
        self.op2 = CSRStorage(8)
        self.sum = CSRStatus(8)
        self.ena = CSRStorage(1, reset = 0)

        self.sync += [ 
            If(self.ena.storage == 1,
                self.sum.status.eq(self.op1.storage + self.op2.storage),
            )
        ] 

# Simple Uart module
class MyUart(Module, AutoCSR):
    def __init__(self, txd, led):
        self.tx_dat = CSRStorage(8)
        self.tx_ena = CSRStorage(1, reset = 0)
        self.tx_bsy = CSRStatus(1)

        tx_status = Signal()

        self.comb += self.tx_bsy.status.eq(tx_status)

        self.specials += [
            Instance("my_uart",
                    i_din=self.tx_dat.storage,
                    i_wr_en=self.tx_ena.storage,
                    i_clk_in=ClockSignal(),
                    o_tx=txd,
                    o_tx_busy=tx_status,
                    )
        ]

    def add_source(self, platform):
            platform.add_source(os.path.join("periphs/verilog/uart", "my_uart.v"))

# Simple wishbone gpio module            
class WbGpio(Module):
    def __init__(self, led):
        self.bus = bus = wishbone.Interface()
        led_wire = Signal(1, reset=1)

        self.comb += led.eq(led_wire)

        # run mw addr 0/1 1 to turn on/off the led
        self.sync += [
            bus.ack.eq(0),
            If(bus.cyc & bus.stb & ~bus.ack,
                bus.ack.eq(1),
                If(bus.we,
                    led_wire.eq(bus.dat_w[0])
                )
            )
        ]

# SJA1000 opencore can controller module
class SJA1000(Module):
    def __init__(self, canif):

        # wishbone bus 
        self.bus = bus = wishbone.Interface()

        self.specials += [
            Instance("can_top",
                    # WB IF
                    i_wb_clk_i   = ClockSignal(),
                    i_wb_rst_i   = ResetSignal(),
                    i_wb_dat_i   = bus.dat_w,
                    o_wb_dat_o   = bus.dat_r,
                    i_wb_cyc_i   = bus.cyc,
                    i_wb_stb_i   = bus.stb,
                    i_wb_we_i    = bus.we, 
                    i_wb_adr_i   = bus.adr,
                    o_wb_ack_o   = bus.ack,
                    # MISC
                    i_clk_i      = ClockSignal("can"),
                    i_rx_i       = canif.rx,
                    o_tx_o       = canif.tx,
                    o_bus_off_on = canif.boo,
                    o_irq_on     = canif.irq,
                    o_clkout_o   = canif.clkout,
                    )
        ]

    def add_source(self, platform):
            platform.add_source(os.path.join("periphs/verilog/can", "can_top.v"))
            platform.add_source(os.path.join("periphs/verilog/can", "can_acf.v"))
            platform.add_source(os.path.join("periphs/verilog/can", "can_btl.v"))
            platform.add_source(os.path.join("periphs/verilog/can", "can_defines.v"))
            platform.add_source(os.path.join("periphs/verilog/can", "can_ibo.v"))
            platform.add_source(os.path.join("periphs/verilog/can", "can_register_asyn.v"))
            platform.add_source(os.path.join("periphs/verilog/can", "can_register_syn.v"))
            platform.add_source(os.path.join("periphs/verilog/can", "can_bsp.v"))
            platform.add_source(os.path.join("periphs/verilog/can", "can_crc.v"))
            platform.add_source(os.path.join("periphs/verilog/can", "can_fifo.v"))
            platform.add_source(os.path.join("periphs/verilog/can", "can_register_asyn_syn.v"))
            platform.add_source(os.path.join("periphs/verilog/can", "can_registers.v"))
            platform.add_source(os.path.join("periphs/verilog/can", "can_register.v"))
