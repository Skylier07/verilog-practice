import cocotb 

import random
from cocotb.triggers import RisingEdge, ReadOnly, FallingEdge, NextTimeStep
from cocotb.clock import Clock

async def reset_dut(dut):
    
    dut.reset.value = 1
    dut.tx_start.value = 0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut.reset.value =0
    await RisingEdge(dut.clk)

async def send_start(dut, data_in):
    dut.tx_data.value = data_in
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)

    dut.tx_start.value = 0

async def wait_clocks(dut, n):
    for _ in range(n):
        await RisingEdge(dut.clk)

async def test_data(dut, data):
    await send_start(dut, data)
    while True:
        await RisingEdge(dut.clk)
        await ReadOnly()

        # if int(dut.tx_busy.value) == 0:
        #     break
        if int(dut.rx_valid.value) == 1:
            break

    assert(int(dut.rx_data.value) == data)


    await NextTimeStep()


@cocotb.test()
async def test_tx(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    for i in range (0, 255):
        await test_data(dut, i)

#     assigned_data  = data

#     await send_start(dut, assigned_data)

#     for _ in range(11):
#         await RisingEdge(dut.clk)
#         await ReadOnly()

#         if (int(dut.tx.value) == 0):
#             break
#     # Testing start
#     assert(int(dut.tx.value) ==0)
#     assert(int(dut.busy.value) == 1)

#     # Test data
#     i = 0
#     while(True):
#         await wait_clocks(dut, 10)
#         await ReadOnly()
#         assert(int(dut.busy.value) == 1)

#         bit = (assigned_data >> i) & 1
#         i+=1
#         print(
#         f"bit {i}: expected={bit}, "
#         f"actual={int(dut.tx.value)}"
# )
#         assert(int(dut.tx.value) ==bit)

#         if(i>7):
#             break




#     await ReadOnly()
#     # Testing idle    
#     assert(int(dut.tx.value) ==1)
#     assert(int(dut.busy.value) ==0)

#     await NextTimeStep()

#     # Test start, data
#     for _ in range(100):
#         data = random.randint(0, 255)

#         await test_data(dut, data)


#     # Test stop
#     await wait_clocks(dut, 10)
#     await ReadOnly()

#     assert(int(dut.busy.value) == 1)
#     assert(int(dut.tx.value) == 1)

#     # Test return idle
#     await wait_clocks(dut, 10)
#     await ReadOnly()
#     assert(int(dut.busy.value) == 0)
#     assert(int(dut.tx.value) == 1)




    