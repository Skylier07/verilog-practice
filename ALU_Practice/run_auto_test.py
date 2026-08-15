from pathlib import Path
from cocotb_tools.runner import get_runner

project_dir = Path(__file__).parent
runner = get_runner("icarus")

runner.build(
    sources=[project_dir/"alu.sv"],
    hdl_toplevel="alu",
    always=True,
)

runner.test(
    hdl_toplevel="alu",
    test_module="alu_auto_tb",
)