import cocotb 

import random
from cocotb.triggers import RisingEdge, ReadOnly, FallingEdge, NextTimeStep
from cocotb.clock import Clock

async def reset_dut(dut):
    
    dut.reset.value = 1
    dut.start.value = 0

    assigned_data  = 0
    dut.data_in.value = assigned_data

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut.reset.value =0
    await RisingEdge(dut.clk)

async def send_start(dut, data_in):
    dut.data_in.value = data_in
    dut.start.value = 1
    await RisingEdge(dut.clk)

    dut.start.value = 0

async def wait_clocks(dut, n):
    for _ in range(n):
        await RisingEdge(dut.clk)

@cocotb.test()
async def test_tx(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)



    await ReadOnly()
    # Testing idle    
    assert(int(dut.tx.value) ==1)
    assert(int(dut.busy.value) ==0)

    await NextTimeStep()
    assigned_data  = 0b10101010

    await send_start(dut, assigned_data)

    for _ in range(11):
        await RisingEdge(dut.clk)
        await ReadOnly()

        if (int(dut.tx.value) == 0):
            break
    # Testing start
    assert(int(dut.tx.value) ==0)
    assert(int(dut.busy.value) == 1)

    # Test data
    i = 0
    while(True):
        await wait_clocks(dut, 10)
        await ReadOnly()
        assert(int(dut.busy.value) == 1)

        bit = (assigned_data >> i) & 1
        i+=1
        assert(int(dut.tx.value) ==bit)

        if(i>7):
            break






    



    # for _ in range(0, 100):
    #     await RisingEdge(dut.clk)
    #     if(is_reset ==1):
    #         expected_count =0
    #         expected_tick = 0
    #     elif(expected_count >=9): #EDIT HERE FOR CLK_PER_BIT 
    #         expected_count =0
    #         expected_tick = 1
    #     else:
    #         expected_count+=1
    #         expected_tick = 0
    #     if(expected_tick):
    #         assert(dut.busy.value ==0)
    #         assert(dut.tx.value ==1)


    
        


    
        