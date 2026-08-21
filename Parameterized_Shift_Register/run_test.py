from pathlib import Path
from cocotb_tools.runner import get_runner
import pytest 

@pytest.mark.parametrize("width", [
    1, 2, 4, 8, 16, 32, 64, 128,
])

def test_shift_register(width):
    project_dir = Path(__file__).parent
    runner = get_runner("icarus")

    runner.build(
        sources=[project_dir/"parameterized_shift_register.sv"],
        hdl_toplevel="shift_register",
        parameters={
            "WIDTH": width,
        },
        build_dir = f"sim_build/test_w_{width}",
        always=True,
    )

    runner.test(
        hdl_toplevel="shift_register",
        test_module="shift_register_tb",
    )