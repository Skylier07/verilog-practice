from pathlib import Path
from cocotb_tools.runner import get_runner

project_dir = Path(__file__).parent
runner = get_runner("icarus")

runner.build(
    sources=[project_dir/"fifo.sv"],
    hdl_toplevel="fifo",
    always=True,
)

runner.test(
    hdl_toplevel="fifo",
    test_module="fifo_tb",
)