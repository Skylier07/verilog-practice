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


BAUD_RATE = 115200
BIT_TIME_NS = round(1000000000/BAUD_RATE)

async def rx(dut):
    await FallingEdge(dut.tx)

    await Timer(BIT_TIME_NS/2, unit="ns")

    assert int(dut.tx.value) ==0

    value = 0

    for i in range(8):
        await Timer(BIT_TIME_NS, unit="ns")

        bit = int(dut.tx.value)
        value = value | bit<<i

    await Timer(BIT_TIME_NS, unit="ns")

    assert int(dut.tx.value) ==1

    return value


@cocotb.test()
async def test_tx_fifo(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    await reset_dut(dut)

    expected = [i*3 for i in range(15)]

    for data in expected:
        await attempt_send(dut, data)

    for expected_data in expected:
        result = await rx(dut)
    
        assert result == expected_data

    # await Timer(2, unit="ms")

