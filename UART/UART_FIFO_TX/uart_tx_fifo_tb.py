import cocotb 

import random
from cocotb.triggers import RisingEdge, ReadOnly, FallingEdge, NextTimeStep, Timer
from cocotb.clock import Clock

async def reset_dut(dut):
    
    dut.reset.value = 1
    dut.write_en.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut.reset.value =0
    await RisingEdge(dut.clk)

async def attempt_send(dut, data):
    dut.write_data.value = data

    dut.write_en.value = 1
    await RisingEdge(dut.clk)
    dut.write_en.value = 0

    await RisingEdge(dut.clk)
    

@cocotb.test()
async def test_tx_fifo(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    for i in range(0, 15):
        await attempt_send(dut, i*3)

