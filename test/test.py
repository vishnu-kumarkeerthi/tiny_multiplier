# test/test.py
import cocotb
from cocotb.triggers import RisingClock
from cocotb.clock import Clock

LOAD_A  = 0
LOAD_B  = 1
START   = 2
OUT_SEL = 3
DONE_BIT = 7
FRAC_BITS = 0  # keep in sync with RTL param

async def pulse(dut, bit):
    dut.uio_in.value = int(dut.uio_in.value) | (1 << bit)
    await RisingClock(dut.clk)
    dut.uio_in.value = int(dut.uio_in.value) & ~(1 << bit)
    await RisingClock(dut.clk)

async def write_A(dut, val):
    dut.ui_in.value = val
    await pulse(dut, LOAD_A)

async def write_B(dut, val):
    dut.ui_in.value = val
    await pulse(dut, LOAD_B)

async def start_mul(dut):
    await pulse(dut, START)

async def read_result(dut):
    # low byte
    dut.uio_in.value = int(dut.uio_in.value) & ~(1 << OUT_SEL)
    await RisingClock(dut.clk)
    lo = int(dut.uo_out.value)

    # high byte
    dut.uio_in.value = int(dut.uio_in.value) | (1 << OUT_SEL)
    await RisingClock(dut.clk)
    hi = int(dut.uo_out.value)

    return (hi << 8) | lo

async def do_test(dut, a, b):
    await write_A(dut, a)
    await write_B(dut, b)
    await start_mul(dut)

    # wait for done (8 cycles typical; give margin)
    for _ in range(64):
        if (int(dut.uio_out.value) >> DONE_BIT) & 1:
            break
        await RisingClock(dut.clk)
    else:
        raise AssertionError(f"Timeout: A={a} B={b}")

    got = await read_result(dut)
    expect = (a * b) >> FRAC_BITS
    assert got == expect, f"A={a:02x} B={b:02x} expect={expect:04x} got={got:04x}"

@cocotb.test()
async def run(dut):
    cocotb.start_soon(Clock(dut.clk, 20, units="ns").start())  # 50MHz
    dut.rst_n.value = 0
    dut.ena.value   = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    await RisingClock(dut.clk); await RisingClock(dut.clk)
    dut.rst_n.value = 1
    dut.ena.value   = 1
    await RisingClock(dut.clk)

    for a, b in [(0x00,0x00),(0x01,0xFF),(0xAA,0x0F),(0x7F,0x80),(0xFF,0xFF),(0x13,0x27)]:
        await do_test(dut, a, b)
