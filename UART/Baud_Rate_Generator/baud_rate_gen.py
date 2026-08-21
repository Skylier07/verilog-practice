from cocotb.triggers import RisingEdge
async def baud_gen_model(clk, reset, CLK_FREQ =10, BAUD_RATE=100):
    count = 0
    CLK_PER_BIT = CLK_FREQ/BAUD_RATE
    while(True):
        await RisingEdge(clk)

        if(reset==1):
            count =0
            tick = 0
        elif(count>=CLK_PER_BIT):
            count =0
            tick = 1
        else:
            count+=1
            tick = 0
        return tick