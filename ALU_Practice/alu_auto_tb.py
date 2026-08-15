import cocotb
from cocotb.triggers import Timer 
from alu import model_alu
import random

@cocotb.test()
async def test_alu(dut):
    for i in range(0, 7):
        dut.op.value=i

        for j in range(100):
            a_val =random.randint(0, 255)
            dut.a.value=a_val
            b_val = random.randint(0,255)
            dut.b.value= b_val



            await Timer(1, unit="ns")

            expected = model_alu(a_val, b_val, i)
            actual = (dut.result.value.to_unsigned(), int(dut.zero.value), int(dut.negative.value), int(dut.carry.value), int(dut.overflow.value))
                        
            

            assert expected == actual,  f"Testing OP: {dut.op.value}, a: {dut.a.value}, b: {dut.b.value}"

 
