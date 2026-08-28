from pathlib import Path
from cocotb_tools.runner import get_runner

project_dir = Path(__file__).parent
uart_dir = project_dir.parent
runner = get_runner("icarus")

runner.build(
    sources=[
        project_dir/"uart_rx_fifo.sv",
        uart_dir/"UART_FIFO_TX"/"uart_tx_fifo.sv",
        # uart_dir/"UART_RX"/"uart_rx.sv",
    ],
    hdl_toplevel="uart_rx_fifo",
    always=True,
)

runner.test(
    hdl_toplevel="uart_rx_fifo",
    test_module="uart_rx_fifo_tb",
)