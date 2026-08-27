import cocotb 
from cocotb.queue import Queue
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

async def monitor_queue(dut, expected_queue):
    while True:
        expected = await expected_queue.get()

        if expected is None:
            return

        result = await rx(dut)

        assert result == expected


async def attempt_send(dut, data):
    dut.write_data.value = data

    dut.write_en.value = 1
    await RisingEdge(dut.clk)
    dut.write_en.value = 0

    await RisingEdge(dut.clk)

async def attempt_send_check(dut, data):
    await FallingEdge(dut.clk)

    dut.write_data.value = data

    dut.write_en.value = 1

    accepted = (int(dut.full.value) ==0)
    await RisingEdge(dut.clk)
    dut.write_en.value = 0

    await ReadOnly()

    return accepted


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

async def monitor_tx(dut, expected):
    for expected_data in expected:
        result = await rx(dut)
        assert result == expected_data


@cocotb.test()
async def test_basic(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    await reset_dut(dut)

    expected = [i*3 for i in range(15)]

    for data in expected:
        await attempt_send(dut, data)

    for expected_data in expected:
        result = await rx(dut)
    
        assert result == expected_data


@cocotb.test()
async def test_full_behavior(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset_dut(dut)

    expected = [j*3 for j in range(20)]
    actual_sent = []
    for data in expected:
        await attempt_send(dut, data)
        if(not dut.full.value):
            actual_sent.append(data)

    for expected_data in actual_sent:
        result = await rx(dut)
    
        assert result == expected_data

@cocotb.test()
async def test_delayed_behavior(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    await reset_dut(dut)

    expected_1 = [1, 2, 3, 4, 5, 6, 7]
    expected_2 = [8, 9, 10, 11, 12]

    expected = expected_1 + expected_2

    monitor = cocotb.start_soon(
        monitor_tx(dut, expected)
    )

    for data in expected_1:
        await attempt_send(dut, data)

    await Timer(30, unit="us")

    for data in expected_2:
        await attempt_send(dut, data)

    await monitor

@cocotb.test()
async def test_fifo_wraparound(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    await reset_dut(dut)

    expected_queue = Queue()

    monitor = cocotb.start_soon(
        monitor_queue(dut, expected_queue)
    )

    tested_data = [i%7 for i in range(100)]

    for data in tested_data:
        if int(dut.full.value):
            await FallingEdge(dut.full)


        accepted = await attempt_send_check(dut, data)

        assert(accepted)

        await expected_queue.put(data)

    await expected_queue.put(None)

    await monitor