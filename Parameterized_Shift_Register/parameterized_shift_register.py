from cocotb.triggers import RisingEdge
async def module_shift_register(width, clk, reset, enable, load, serial_in, parallel_in):
    if(len(parallel_in) != width):
        raise VerilogError("Parallel_in has a different size to width")

    while(True):
        await RisingEdge(clk)

        if(reset):
            q = 0
        elif(load):
            q = parallel_in
        elif(enable):
            q = (q>>1) | (serial_in<<(width-1))
        return q



class VerilogError(Exception):
    pass