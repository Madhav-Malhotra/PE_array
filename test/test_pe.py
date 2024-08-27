import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

clocks_per_phase = 10

async def reset(dut):
    # Zeroo all inputs
    dut.act.value = 0
    dut.wgt.value = 0
    dut.store.value = 0
    dut.reuse.value = 0
    dut.addr.value = 0
    dut.finish.value = 0

    # Reset the DUT
    dut.reset.value   = 1

    # Wait for reset to stabilise
    await ClockCycles(dut.clk, 5)
    
    # Deassert the reset
    dut.reset.value = 0

    await ClockCycles(dut.clk, 5)

@cocotb.test()
async def test_all(dut):
    # Start a clock
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Test reset
    await reset(dut)
    assert dut.out == 0
    for i in range(4):
        assert dut.regfile[i] == 0

    # Test multiplications without regfile or dot products
    for _ in range(10):
        dut.act.value = random.randint(0, 255)
        dut.wgt.value = random.randint(0, 255)
        dut.finish.value = 1
        await ClockCycles(dut.clk, 1)
        assert dut.out == dut.act * dut.wgt
    
    await reset(dut)

    # Test multiplications without regfile but with dot products
    total = 0
    for _ in range(10):
        dut.act.value = random.randint(0, 255)
        dut.wgt.value = random.randint(0, 255)
        dut.finish.value = 0
        total = total + dut.act * dut.wgt

        await ClockCycles(dut.clk, 1)
        assert dut.regfile[0] == total
    
    # Last cycle to finish the dot product
    dut.act.value = random.randint(0, 255)
    dut.wgt.value = random.randint(0, 255)
    dut.finish.value = 1
    total = total + dut.act * dut.wgt

    await ClockCycles(dut.clk, 1)
    assert dut.out == total
    assert dut.regfile[0] == 0

    await reset(dut)

    # Test multiplications with regfile and dot products
    total = 0

    # Generate a weight
    dut.finish.value = 0
    dut.act.value = random.randint(0, 255)
    dut.wgt.value = random.randint(0, 255)
    total = total + dut.act * dut.wgt
    
    # Store weight in regfile[1]
    dut.store.value = 1
    dut.addr.value = 1

    # Check multiplication and weight storage
    await ClockCycles(dut.clk, 1)
    assert dut.regfile[0] == total
    assert dut.regfile[1] == dut.wgt.value

    # Check weight reuse with new activations
    for _ in range(10):
        dut.act.value = random.randint(0, 255)
        dut.store.value = 0
        dut.reuse.value = 1
        dut.addr.value = 1

        total = total + dut.act * dut.regfile[1]
        await ClockCycles(dut.clk, 1)
        assert dut.regfile[0] == total

    # Last cycle to finish the dot product
    dut.act.value = random.randint(0, 255)
    dut.wgt.value = random.randint(0, 255)
    data.reuse.value = 0
    dut.finish.value = 1
    total = total + dut.act * dut.wgt

    await ClockCycles(dut.clk, 1)
    assert dut.out == total
    assert dut.regfile[0] == 0

    await reset(dut)