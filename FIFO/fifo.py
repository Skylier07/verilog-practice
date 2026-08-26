from cocotb.triggers import RisingEdge

async def fifo_model(clk, reset, write_en, write_data, read_en, DEPTH):
    write_ptr =0
    read_ptr=0
    count =0
    empty =1
    full =0
    mem =[]
    while True:
        await RisingEdge(clk)
        if(reset):
            write_ptr -0
            read_ptr =0
            count =0
            empty =1
            full =0
        if(write_en and not full):
            mem[write_ptr] = write_data
            count+=1
            if(write_ptr>=DEPTH):
                write_ptr=0
            else:
                write_ptr+=1
        if(read_en and not empty):
            read_data = mem[read_ptr] 
            count -=1
            if(read_ptr>=DEPTH):
                read_ptr = 0
            else:
                read_ptr+=1

        if(count >= (DEPTH-1)):
            full = 1
        elif(count<=0):
            empty =1
        else:
            empty =0
            full =0
        
        return read_data, full, empty