import cocotb 

import random
from cocotb.triggers import RisingEdge, ReadOnly, FallingEdge, NextTimeStep, Timer
from cocotb.clock import Clock

BAUD_RATE = 115200
BIT_TIME_NS = round(1000000000/BAUD_RATE)

async def reset_dut(dut):
    dut.reset.value = 1
    dut.rx.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.reset.value =0
    await RisingEdge(dut.clk)

async def send_false_start(dut):
    dut.rx.value=0
    await(Timer(1, unit="us"))

    dut.rx.value=1
    await(Timer(5, unit="us"))

async def wait_one_bit():
    await(Timer(BIT_TIME_NS, unit="ns"))

async def drive_uart(dut, value):
    # start

    dut.rx.value = 0
    await wait_one_bit()

    for i in range(8):
        dut.rx.value = (value >> i) & 1
        await wait_one_bit()

    dut.rx.value=1

async def drive_and_test(dut, value):
    await drive_uart(dut, value)
    await RisingEdge(dut.data_valid)
    await ReadOnly()

    assert(int(dut.data_out.value) == value)
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert(int(dut.data_valid.value) ==0)


@cocotb.test()
async def test_rx(dut):
    cocotb.start_soon(Clock(dut.clk,20, unit="ns").start())
    await reset_dut(dut)
    await ReadOnly()
    assert(int(dut.data_valid.value) ==0)
    assert(int(dut.data_out.value) ==0)
    await NextTimeStep()

    await send_false_start(dut)

    await Timer(BIT_TIME_NS, unit="ns")

    assert (int(dut.data_valid.value) ==0)
    # assert(int(dut.))

    for i in range(0, 255):
        await drive_and_test(dut, i)
        await NextTimeStep()

