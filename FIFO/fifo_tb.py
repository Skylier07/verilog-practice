import cocotb 

import random
from cocotb.triggers import RisingEdge, ReadOnly, FallingEdge, NextTimeStep, Timer
from cocotb.clock import Clock
from collections import deque
from fifo import fifo_model

q = deque()

async def reset_dut(dut):
    dut.reset.value = 1
    dut.write_en.value = 0
    dut.read_en.value =0
    dut.write_data.value =0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.reset.value =0
    await RisingEdge(dut.clk)

async def attempt_write(dut, data):
    dut.write_en.value = 1
    dut.write_data.value = data
    await RisingEdge(dut.clk)
    await ReadOnly()
    await NextTimeStep()
    dut.write_en.value = 0
    await RisingEdge(dut.clk)

async def attempt_read(dut):
    dut.read_en.value = 1
    await RisingEdge(dut.clk)
    await ReadOnly()
    await NextTimeStep()
    dut.read_en.value = 0
    await RisingEdge(dut.clk)

    return int(dut.read_data.value)



async def fifo_full(dut):
    return bool(dut.full.value)

async def fifo_empty(dut):
    return bool(dut.empty.value)



@cocotb.test()
async def test_rx(dut):
    cocotb.start_soon(Clock(dut.clk,20, unit="ns").start())

    # Initial full fill full drain test
    await reset_dut(dut)

    await ReadOnly()
    await NextTimeStep()

    for i in range (0, 16):
        q.append(i)

        await attempt_write(dut, i)

    assert(await fifo_full(dut))
    for i in range(0, 15):
        assert(await attempt_read(dut) == q.popleft())

    assert(not await fifo_empty(dut))
    assert(await attempt_read(dut) == q.popleft())
    assert(await fifo_empty(dut))


    # Wrap around test

    await ReadOnly()
    await NextTimeStep()

    for i in range (0, 12):
        q.append(i)
        await attempt_write(dut, i)

    assert(not await fifo_full(dut))
    for i in range(0, 10):
        assert(await attempt_read(dut) == q.popleft())

    for i in range (0, 12):
        q.append(i)
        await attempt_write(dut, i)

    for i in range(0, 14):
        assert(await attempt_read(dut) == q.popleft())


    # Full / Empty behavior 
    for i in range (0, 25):
        if(i<=15):
            q.append(i)
        await attempt_write(dut, i)

    assert(await fifo_full(dut))


    for i in range(0, 15):
        assert(await attempt_read(dut) == q.popleft())