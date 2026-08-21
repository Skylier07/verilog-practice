from pathlib import Path
from cocotb_tools.runner import get_runner

project_dir = Path(__file__).parent
runner = get_runner("icarus")

runner.build(
    sources=[project_dir/"baud_rate_gen.sv"],
    hdl_toplevel="baud_gen",
    always=True,
)

runner.test(
    hdl_toplevel="baud_gen",
    test_module="baud_gen_tb",
)