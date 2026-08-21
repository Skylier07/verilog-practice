import cocotb

from parameterized_shift_register import module_shift_register
import random
from cocotb.triggers import RisingEdge, ReadOnly, FallingEdge
from cocotb.clock import Clock


@cocotb.test()
async def test_shift(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.reset.value = 1
    dut.load.value = 0
    dut.enable.value = 0
    dut.serial_in.value = 0
    dut.parallel_in.value = 0

    await RisingEdge(dut.clk)
    await ReadOnly()

    for _ in range(100):
        await FallingEdge(dut.clk)
        previous_q = int(dut.q.value)

        # set_width = random.randint(1, 128) Cannot set width with DUT
        width = len(dut.q)
        set_parallel_in = random.randint(0, (2**width)-1)

        dut.parallel_in.value = set_parallel_in
        is_reset = random.randint(0, 1)
        dut.reset.value = is_reset

        is_load = random.randint(0, 1)
        dut.load.value = is_load

        is_enable = random.randint(0, 1)
        dut.enable.value = is_enable

        set_serial_in = random.randint(0, 1)
        dut.serial_in.value = set_serial_in
        
        await RisingEdge(dut.clk)
        await ReadOnly()

        if(is_reset):
            assert(int(dut.q.value) == 0), f"Is reset triggered: {dut.reset.value}; q value: {dut.q.value}"

        elif(is_load):
            assert(int(dut.q.value) == set_parallel_in), f"Is load triggered: {dut.load.value}; q value: {dut.q.value}; in value: {set_parallel_in}"
        elif(is_enable):
            assert(int(dut.q.value) ==  (previous_q>>1) | (set_serial_in<<(width-1))), f"Is enable triggered: {dut.enable.value}; q value: {dut.q.value}; previous value: {previous_q}; serial in value: {dut.serial_in.value}"

        else:
            assert(int(dut.q.value) == previous_q), f"Is enable triggered: {dut.enable.value}; q value: {dut.q.value}; previous value: {previous_q}"


