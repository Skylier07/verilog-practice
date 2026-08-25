import cocotb 

import random
from cocotb.triggers import RisingEdge, ReadOnly, FallingEdge, NextTimeStep
from cocotb.clock import Clock


async def reset_dut(dut):
    dut.reset.value = 1
    dut.rx.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.reset.value =0
    await RisingEdge(dut.clk)

async def send_false_start(dut):
    dut.rx.value=0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rx.value=1
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_rx(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    reset_dut(dut)

    send_false_start(dut)
    # assert(int(dut.))