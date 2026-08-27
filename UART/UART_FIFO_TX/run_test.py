from pathlib import Path
from cocotb_tools.runner import get_runner

project_dir = Path(__file__).parent
runner = get_runner("icarus")

runner.build(
    sources=[project_dir/"uart_tx_fifo.sv"],
    hdl_toplevel="uart_tx_fifo",
    always=True,
    waves=True,
)

runner.test(
    hdl_toplevel="uart_tx_fifo",
    test_module="uart_tx_fifo_tb",
    waves=True,
    gui=True,
)