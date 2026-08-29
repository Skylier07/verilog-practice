import cocotb 

import random
from cocotb.triggers import RisingEdge, ReadOnly, FallingEdge, NextTimeStep, Timer
from cocotb.clock import Clock
from collections import deque

expected = deque()

async def reset_dut(dut):
    
    dut.reset.value = 1
    dut.tx_write_en.value = 0
    dut.rx_read_en.value = 0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut.reset.value =0
    await RisingEdge(dut.clk)

async def attempt_send(dut, data):
    await FallingEdge(dut.clk)
    dut.tx_write_data.value = data

    dut.tx_write_en.value = 1
    await RisingEdge(dut.clk)
    dut.tx_write_en.value = 0

async def wait_for_rx(dut, timeout_cycles=10000):
    for _ in range(timeout_cycles):
        await RisingEdge(dut.clk)
        await ReadOnly()

        if int(dut.rx_empty.value) ==0:
            return

    assert False

async def attempt_read(dut):
    await FallingEdge(dut.clk)
    dut.rx_read_en.value = 1

    await RisingEdge(dut.clk)
    await ReadOnly()

    result = int(dut.rx_read_data.value)

    await FallingEdge(dut.clk)

    dut.rx_read_en.value = 0
    return result

async def wait_for_bytes(dut, bytes):
    received = 0

    while received < bytes:
        await RisingEdge(dut.clk)
        await ReadOnly()

        if int(dut.rx_data_valid.value):
            received += 1

    await RisingEdge(dut.clk)
    await ReadOnly()
    await NextTimeStep()

async def aggresive_drain(dut):
    for _ in range(10):
        if (int(dut.rx_empty.value) == 1):
            return
        
        await FallingEdge(dut.clk)
        dut.rx_read_en.value = 1

        await RisingEdge(dut.clk)
        await ReadOnly()

        result = int(dut.rx_read_data.value)
        assert result == expected.popleft()
        await FallingEdge(dut.clk)
        

        dut.rx_read_en.value = 0

async def attempt_send_and_record(dut, data):
    await FallingEdge(dut.clk)
    if(dut.tx_full.value == 1):
        return False
    else:
        dut.tx_write_data.value = data
        dut.tx_write_en.value = 1
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)
        dut.tx_write_en.value= 0

        expected.append(data)

        return True

async def one_tick_valid(dut):
    prev_valid = 0

    while True:
        await RisingEdge(dut.clk)
        await ReadOnly()

        current_valid = int(dut.rx_data_valid.value)
        assert not (prev_valid and current_valid)

        prev_valid = current_valid

@cocotb.test()
async def test_simple_behaviors(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    cocotb.start_soon(one_tick_valid(dut))

    await reset_dut(dut)

    await ReadOnly()
    await NextTimeStep()

    await attempt_send(dut, 0)

    await wait_for_rx(dut)
    
    assert(int(dut.rx_empty) ==0)

    assert(await attempt_read(dut) == 0)


@cocotb.test()
async def test_multi_byte_ordering(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    await reset_dut(dut)

    await ReadOnly()
    await NextTimeStep()

    for j in range (0, 10):
        
        await attempt_send(dut, j*3)


    await wait_for_bytes(dut, 10)

    for j in range(0, 10):
        assert(await attempt_read(dut) == j*3)


@cocotb.test()
async def test_full(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    await reset_dut(dut)

    await ReadOnly()
    await NextTimeStep()

    for j in range (0, 16):
        
        await attempt_send(dut, j*3)


    await wait_for_bytes(dut, 16)

    assert(int(dut.rx_full.value) == 1)

    await attempt_send(dut, 250)

    for j in range(0, 16):
        assert(await attempt_read(dut) == j*3)

    assert(int(dut.rx_empty.value) == 1)


@cocotb.test()
async def test_drain_refill(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    await reset_dut(dut)

    await ReadOnly()
    await NextTimeStep()

    for j in range(9):
        await attempt_send(dut, j)

    await wait_for_bytes(dut, 9)

    for j in range(9):
        assert(await attempt_read(dut) == j)

    assert int(dut.rx_empty.value) == 1

    for j in range(9):
        await attempt_send(dut, 50+j)

    await wait_for_bytes(dut, 9)

    for j in range(9):
        assert(await attempt_read(dut) == (j+50))

    assert int(dut.rx_empty.value) == 1


@cocotb.test()
async def random_stream(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    await reset_dut(dut)

    await ReadOnly()
    await NextTimeStep()

    for _ in range(0, 100):
        byte = random.randint(0, 255)

        while int(dut.tx_full.value):
            await RisingEdge(dut.clk)

        await attempt_send(dut, byte)
        expected.append(byte)

        if(random.randint(0, 20)<3 and (int(dut.rx_empty.value)==0)):
            result = await attempt_read(dut)
            assert result == expected.popleft()


@cocotb.test()
async def hostile_random_test(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    await reset_dut(dut)

    await ReadOnly()
    await NextTimeStep()

    sent = 0
    expected.clear()

    while sent < 1000:
        if (int(dut.rx_full.value) ==1):
            await aggresive_drain(dut)



        data = random.randint(0, 255)
        if(await attempt_send_and_record(dut, data)):
            sent+=1

        await RisingEdge(dut.clk)


    while expected:
        await wait_for_rx(dut)

        result = await attempt_read(dut)

        assert(result == expected.popleft())

    assert(int(dut.rx_empty.value) == 1)



@cocotb.test()
async def reset_test(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    await reset_dut(dut)

    await ReadOnly()
    await NextTimeStep()

    sent = 0
    expected.clear()

    while sent < 1000:
        if (int(dut.rx_full.value) ==1):
            await aggresive_drain(dut)

        if random.randint(0, 25) == 5:
            break

        data = random.randint(0, 255)
        if(await attempt_send_and_record(dut, data)):
            sent+=1

        await RisingEdge(dut.clk)


    await reset_dut(dut)

    await ReadOnly()
    await NextTimeStep()

    assert dut.rx_empty.value == 1

    expected.clear()

    while sent < 100:
        if (int(dut.rx_full.value) ==1):
            await aggresive_drain(dut)



        data = random.randint(0, 255)
        if(await attempt_send_and_record(dut, data)):
            sent+=1

        await RisingEdge(dut.clk)


    while expected:
        await wait_for_rx(dut)

        result = await attempt_read(dut)

        assert(result == expected.popleft())

    assert(int(dut.rx_empty.value) == 1)
