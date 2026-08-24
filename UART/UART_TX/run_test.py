from pathlib import Path
from cocotb_tools.runner import get_runner

project_dir = Path(__file__).parent
runner = get_runner("icarus")

runner.build(
    sources=[project_dir/"uart_tx.sv"],
    hdl_toplevel="uart_top",
    always=True,
)

runner.test(
    hdl_toplevel="uart_top",
    test_module="uart_tx_tb",
)