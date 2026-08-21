## Project specification

Use this interface:
```
module baud_gen #(
    parameter CLK_FREQ  = 50_000_000,
    parameter BAUD_RATE = 115_200
)(
    input  logic clk,
    input  logic reset,
    output logic tick
);
```
This matches the intended Phase 4 component interface.

Required behavior
| Situation | Required result |
|---|---|
| reset = 1 on rising clock edge | Counter resets and tick = 0 |
| Normal operation | Internal counter increments every clk rising edge |
| Counter reaches end of UART bit period | Counter returns to zero and tick = 1 |
| Next clock cycle | tick returns to 0 |
| Parameters change | Design automatically adjusts its counter size/timing |



For this first version, define:
`
CLKS_PER_BIT = CLK_FREQ / BAUD_RATE
`
using integer division.

For the default values:
`
CLKS_PER_BIT = 434
`
Your counter therefore needs to represent approximately:
`
0 ... 433
`
After counting 434 clock edges, generate the pulse and restart.

That last detail matters because it prevents the classic off-by-one bug:
`
0 → 1 → ... → 433 → tick
`
is 434 cycles.