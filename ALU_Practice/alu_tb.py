import cocotb
from cocotb.triggers import Timer 

@cocotb.test()
async def test_alu(dut):
    dut.a.value = 5
    dut.b.value = 10
    dut.op.value = 0b000


    await Timer(1, unit="ns")

    assert dut.result.value == 15

    dut.a.value=10
    dut.b.value =5

    dut.op.value=0b001

    await Timer(1, unit="ns")

    assert dut.result.value == 5

    dut.a.value = 0b10110100
    dut.b.value = 0b10110001

    dut.op.value = 0b010

    await Timer(1, unit="ns")

    assert dut.result.value == 0b10110000

    dut.a.value = 0b10110100
    dut.b.value = 0b10110001

    dut.op.value = 0b011

    await Timer(1, unit="ns")

    assert dut.result.value == 0b10110101

    dut.a.value = 0b10110100
    dut.b.value = 0b10110001

    dut.op.value = 0b011

    await Timer(1, unit="ns")

    assert dut.result.value == 0b10110101

    dut.a.value = 0b10110100
    dut.b.value = 0b10110001

    dut.op.value = 0b100

    await Timer(1, unit="ns")

    assert dut.result.value == 0b00000101

    dut.a.value = 0b10110100

    dut.op.value = 0b101

    await Timer(1, unit="ns")

    assert dut.result.value == 0b01101000


    dut.a.value = 0b10110100

    dut.op.value = 0b110

    await Timer(1, unit="ns")

    assert dut.result.value == 0b01011010



    dut.a.value = 0b10110100
    dut.b.value = 0b01001000


    dut.op.value = 0b111

    await Timer(1, unit="ns")

    assert dut.result.value == 0b0
