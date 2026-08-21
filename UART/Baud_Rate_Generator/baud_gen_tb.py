import cocotb 

# from baud_rate_gen import baud_gen_model
import random
from cocotb.triggers import RisingEdge, ReadOnly, FallingEdge
from cocotb.clock import Clock

@cocotb.test()
async def test_baud(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.reset.value = 1

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    is_reset = 0
    dut.reset.value = is_reset
    expected_count = 0
    expected_tick = 0

    for _ in range (10000):

        if(random.randint(0, 300) == 0):
            is_reset = 1
        else:
            is_reset =0

        await RisingEdge(dut.clk)
        if(is_reset ==1):
            expected_count =0
            expected_tick = 0
        elif(expected_count >= 10): #EDIT HERE FOR CLK_PER_BIT 
            expected_count =0
            expected_tick = 1
        else:
            expected_count+=1
            expected_tick = 0

        assert(int(dut.tick.value) == expected_tick)
        


    