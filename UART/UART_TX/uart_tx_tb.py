import cocotb 

import random
from cocotb.triggers import RisingEdge, ReadOnly, FallingEdge, NextTimeStep
from cocotb.clock import Clock

@cocotb.test()
async def test_tx(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.reset.value = 1
    dut.start.value = 0

    assigned_data  = 0b10101010
    dut.data_in.value = assigned_data

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut.reset.value =0
    await ReadOnly()

    is_reset =0
    for _ in range(0, 1000):
        await RisingEdge(dut.clk)

        
        assert(dut.tx.value ==1)
        assert(dut.busy.value ==0)


    dut.start.value = 1
    

    while True:
        await RisingEdge(dut.clk)

        if(is_reset ==1):
            expected_count =0
            expected_tick = 0
        elif(expected_count >=9): #EDIT HERE FOR CLK_PER_BIT 
            expected_count =0
            expected_tick = 1
        else:
            expected_count+=1
            expected_tick = 0

        if(expected_tick):
            assert(dut.tx.value ==0)
            assert(dut.busy.value ==1)
            break

    i =7
    while(True):
        await RisingEdge(dut.clk)
        assert(dut.busy.value ==1)
        if(is_reset ==1):
            expected_count =0
            expected_tick = 0
        elif(expected_count >=9): #EDIT HERE FOR CLK_PER_BIT 
            expected_count =0
            expected_tick = 1
        else:
            expected_count+=1
            expected_tick = 0
        if(expected_tick):
            bit = (assigned_data >> i) & 1
            i=i-1
            assert(dut.tx.value ==bit)

        if(i<0):
            break

    for _ in range(0, 100):
        await RisingEdge(dut.clk)
        if(is_reset ==1):
            expected_count =0
            expected_tick = 0
        elif(expected_count >=9): #EDIT HERE FOR CLK_PER_BIT 
            expected_count =0
            expected_tick = 1
        else:
            expected_count+=1
            expected_tick = 0
        if(expected_tick):
            assert(dut.busy.value ==0)
            assert(dut.busy.value ==1)


    
        


    
        