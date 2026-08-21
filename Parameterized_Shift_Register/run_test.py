from pathlib import Path
from cocotb_tools.runner import get_runner

project_dir = Path(__file__).parent
runner = get_runner("icarus")

runner.build(
    sources=[project_dir/"parameterized_shift_register.sv"],
    hdl_toplevel="shift_register",
    always=True,
)

runner.test(
    hdl_toplevel="shift_register",
    test_module="shift_register_tb",
)