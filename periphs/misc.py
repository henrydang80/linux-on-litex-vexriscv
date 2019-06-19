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

# CanController module
class CanController(Module):
    def __init__(self):
             
        port_0_io = Signal(7)
        tx_o = Signal()        
        irq_on = Signal()
        clkout_o = Signal()
        bus_off_on = Signal()
        
        self.specials += [
            Instance("can_top",
                    i_rst_i=0,
                    i_ale_i=0,
                    i_rd_i=0,
                    i_wr_i=0,
                    io_port_0_io=port_0_io,
                    i_cs_can_i=0,
                    i_clk_i=ClockSignal(),
                    i_rx_i=0,
                    o_tx_o=tx_o,
                    o_bus_off_on=bus_off_on,
                    o_irq_on=irq_on,
                    o_clkout_o=clkout_o,
                    )
        ]        
        