import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

async def reset(dut):
    # Zero all inputs
    dut.act.value = 0
    dut.wgt.value = 0
    dut.store.value = 0
    dut.reuse.value = 0
    dut.addr.value = 0
    dut.finish.value = 0

    # Reset the DUT
    dut.rst.value   = 1

    # Wait for reset to stabilise
    await ClockCycles(dut.clk, 5)
    
    # Deassert the reset
    dut.rst.value = 0

    await ClockCycles(dut.clk, 5)

@cocotb.test()
async def test_reset(dut):
    # Start a clock
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    await reset(dut)
    
    # Check that reset cleared internal regfile and output
    assert dut.out == 0
    for i in range(4):
        assert dut.regfile[i] == 0

    await reset(dut)

@cocotb.test()
async def test_multiplication_no_regfile_no_dot(dut):
    # Start a clock
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    await reset(dut)

    # Run ten tests
    for _ in range(1):
        # Generate random activations and weights
        dut.act.value = random.randint(0, 255)
        dut.wgt.value = random.randint(0, 255)

        # Prevent dot product from accumulating
        dut.finish.value = 1

        # Check that output is product of act and wgt
        await ClockCycles(dut.clk, 3)
        assert dut.out.value == dut.act.value * dut.wgt.value
    
    await reset(dut)

@cocotb.test()
async def test_multiplication_no_regfile_with_dot(dut):
    # Start a clock
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    await reset(dut)

    # Run ten tests
    total = 0
    for _ in range(10):
        # Generate random activations and weights
        dut.act.value = random.randint(0, 255)
        dut.wgt.value = random.randint(0, 255)

        # Accumulate dot product
        dut.finish.value = 0
        total = total + dut.act.value * dut.wgt.value

        # Check that output is MAC of act and wgt
        await ClockCycles(dut.clk, 1)
        assert dut.regfile[0].value == total
    
    # Last cycle to finish the dot product
    dut.act.value = random.randint(0, 255)
    dut.wgt.value = random.randint(0, 255)
    dut.finish.value = 1
    total = total + dut.act.value * dut.wgt.value

    # Check that output is as expected and regfile prepped for next dot product
    await ClockCycles(dut.clk, 1)
    assert dut.out.value == total
    assert dut.regfile[0].value == 0

    await reset(dut)



@cocotb.test()
async def test_multiplication_with_regfile_with_dot(dut):
    # Start a clock
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial conditions
    await reset(dut)
    total = 0

    # Start accumulating dot product with random weight and activation
    dut.finish.value = 0
    dut.act.value = random.randint(0, 255)
    dut.wgt.value = random.randint(0, 255)
    total = total + dut.act.value * dut.wgt.value
    
    # Store weight in regfile[1]
    dut.store.value = 1
    dut.addr.value = 1

    # Check product as expected and weight storage
    await ClockCycles(dut.clk, 1)
    assert dut.regfile[0].value == total
    assert dut.regfile[1].value == dut.wgt.value

    # Check weight reuse with new activations
    for _ in range(10):
        dut.act.value = random.randint(0, 255)
        dut.store.value = 0
        dut.reuse.value = 1
        dut.addr.value = 1

        total = total + dut.act.value * dut.regfile[1].value
        await ClockCycles(dut.clk, 1)
        assert dut.regfile[0].value == total

    # Last cycle to finish the dot product
    dut.act.value = random.randint(0, 255)
    dut.wgt.value = random.randint(0, 255)
    data.reuse.value = 0
    dut.finish.value = 1
    total = total + dut.act.value * dut.wgt.value

    await ClockCycles(dut.clk, 1)
    assert dut.out.value == total
    assert dut.regfile[0].value == 0

    await reset(dut)