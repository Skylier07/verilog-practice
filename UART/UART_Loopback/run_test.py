from pathlib import Path
from cocotb_tools.runner import get_runner

project_dir = Path(__file__).parent
runner = get_runner("icarus")

runner.build(
    sources=[project_dir/"uart_loopback.sv"],
    hdl_toplevel="uart_loopback",
    always=True,
    waves=True,
)

runner.test(
    hdl_toplevel="uart_loopback",
    test_module="uart_loopback_tb",
    waves=True,
    gui=True,
)