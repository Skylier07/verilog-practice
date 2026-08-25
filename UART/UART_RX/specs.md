# UART RX Specification

## 1. Purpose

Implement a parameterized UART receiver module named `uart_rx`.

The receiver accepts a standard asynchronous UART serial stream and reconstructs each valid 8-bit frame into a parallel byte.

This milestone uses:

- 8 data bits
- no parity
- 1 stop bit
- LSB-first transmission
- idle-high UART line
- mid-bit sampling
- one-cycle `data_valid` pulse

Do not add FIFO logic, oversampling, parity, configurable frame formats, or advanced error reporting in this module.

---

## 2. Module Interface

```systemverilog
module uart_rx #(
    parameter CLK_FREQ  = 50_000_000,
    parameter BAUD_RATE = 115200
)(
    input  logic       clk,
    input  logic       reset,
    input  logic       rx,

    output logic [7:0] data_out,
    output logic       data_valid
);
```

### Parameters

#### `CLK_FREQ`

Frequency of the system clock in Hz.

Example:

```text
50_000_000
```

means a 50 MHz system clock.

#### `BAUD_RATE`

UART baud rate in bits per second.

Example:

```text
115200
```

---

## 3. UART Frame Format

The receiver must accept an 8-N-1 UART frame:

```text
idle    start      8 data bits, LSB first       stop    idle

  1       0      d0 d1 d2 d3 d4 d5 d6 d7         1       1
```

A complete valid frame contains:

1. one start bit: `0`
2. eight data bits
3. one stop bit: `1`

The data bits arrive least-significant-bit first.

For example, transmitting:

```text
8'b10110010
```

produces this serial data-bit order:

```text
bit 0 = 0
bit 1 = 1
bit 2 = 0
bit 3 = 0
bit 4 = 1
bit 5 = 1
bit 6 = 0
bit 7 = 1
```

---

## 4. Clock Cycles Per UART Bit

Derive the approximate number of system-clock cycles in one UART bit period:

```systemverilog
localparam CLKS_PER_BIT = CLK_FREQ / BAUD_RATE;
```

For example:

```text
CLK_FREQ  = 50,000,000 Hz
BAUD_RATE = 115,200 baud

CLKS_PER_BIT ≈ 434
```

Integer division is acceptable for this milestone.

---

## 5. Required Internal State

The design should contain enough registered state to track at least:

- current RX state
- clock-cycle count within a UART bit
- current data-bit index
- partially received byte

Suggested conceptual names:

```text
state
clk_count
bit_index
data_reg
```

Exact names and widths are up to the implementation.

Counters should be wide enough for the configured parameter values.

---

## 6. Required Receiver States

Use an FSM with the following logical states:

```text
IDLE
START
DATA
STOP
```

Equivalent naming is acceptable.

A separate `DONE` or `CLEANUP` state is optional but is not required.

Conceptually:

```text
IDLE
  |
  | possible start bit detected
  v
START
  |
  | valid start bit confirmed
  v
DATA
  |
  | 8 data bits sampled
  v
STOP
  |
  | frame accepted or rejected
  v
IDLE
```

---

## 7. Reset Behavior

`reset` is synchronous and active-high.

On reset, the receiver must return to a clean idle condition.

Required effects:

```text
state      -> IDLE
data_valid -> 0
clk_count  -> initial value
bit_index  -> initial value
```

`data_out` may be cleared to `0`.

The module must not report a received byte as a result of reset.

---

## 8. IDLE Behavior

A UART line is idle when:

```text
rx = 1
```

While idle:

- remain in `IDLE`
- keep `data_valid = 0`
- wait for `rx` to become `0`

When `rx == 0`, treat this as a **possible** start bit and begin start-bit validation.

Do not immediately treat the falling signal as a confirmed frame.

---

## 9. Start-Bit Validation

The receiver must sample the start bit near its center.

After detecting that `rx` has gone low:

1. begin counting system-clock cycles
2. wait approximately half of one UART bit period
3. sample `rx`

Conceptually:

```text
|------------- START BIT -------------|

0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
                ^
              sample
```

Use approximately:

```text
CLKS_PER_BIT / 2
```

system-clock cycles.

### Valid Start Bit

If the midpoint sample is:

```text
rx == 0
```

the start bit is valid.

Proceed to receive the data bits.

### False Start

If the midpoint sample is:

```text
rx == 1
```

the low pulse was not a valid start bit.

Required behavior:

- abandon the frame
- return to `IDLE`
- do not assert `data_valid`

---

## 10. Data-Bit Sampling

Once the start bit has been validated, sample one data bit every full UART bit period.

The receiver should therefore wait approximately:

```text
CLKS_PER_BIT
```

system-clock cycles between each data sample.

Sample near the middle of each data bit.

Receive exactly eight bits.

The first received data bit must be stored as:

```text
data_reg[0]
```

The last received data bit must be stored as:

```text
data_reg[7]
```

The bit index should therefore progress:

```text
0
1
2
3
4
5
6
7
```

After bit 7 has been sampled, proceed to the stop bit.

---

## 11. Stop-Bit Validation

After receiving data bit 7:

1. wait approximately one full UART bit period
2. sample the stop bit

A valid stop bit is:

```text
rx == 1
```

### Valid Stop Bit

If the stop bit is high:

- accept the received byte
- update `data_out`
- assert `data_valid` for one system-clock cycle
- return to `IDLE`

### Invalid Stop Bit

If the stop bit is low:

- reject the frame
- do not assert `data_valid`
- return to `IDLE`

No separate `framing_error` output is required for this milestone.

---

## 12. `data_out` Behavior

`data_out` contains the most recently accepted UART byte.

It only needs to change when a complete valid frame has been received.

A malformed frame must not be reported as a new byte.

The value of `data_out` between valid receptions is not considered a new transaction unless accompanied by `data_valid`.

---

## 13. `data_valid` Behavior

`data_valid` is a pulse indicating:

> A complete new byte has just been received successfully.

It must remain high for exactly one `clk` cycle per valid byte.

Expected shape:

```text
clk        _/‾\_/‾\_/‾\_/‾\_/‾\_

data_valid ________/‾\____________
                   one cycle
```

It must be low:

- while idle
- while receiving a frame
- after a false start
- after an invalid stop bit
- on the cycle after a valid pulse

Do not hold `data_valid` high until another byte arrives.

---

## 14. Timing Model

For this milestone, the receiver may assume:

- transmitter baud rate closely matches `BAUD_RATE`
- one system clock drives all RX logic
- no parity
- one stop bit
- no severe line noise
- no large baud-rate mismatch

The UART input is asynchronous relative to `clk`, so the start transition does not have to occur exactly on a system-clock edge.

The receiver should tolerate reasonable phase differences between the beginning of a UART frame and the local `clk`.

---

## 15. Out of Scope

Do **not** implement these yet:

- 16x oversampling
- majority-vote sampling
- parity
- configurable number of data bits
- configurable stop bits
- break detection
- framing-error output
- FIFO
- flow control
- RTS/CTS
- AXI-style interfaces
- runtime-configurable baud rate
- autobaud detection

These can be future extensions.

---

## 16. Cocotb Verification Requirements

Create independent RX verification before connecting the RTL transmitter.

The cocotb testbench should directly drive `rx`.

### Required helper

Create a helper conceptually equivalent to:

```python
async def send_uart_byte(dut, value):
    ...
```

The helper should drive:

```text
idle = 1
start = 0
8 data bits, LSB first
stop = 1
```

using the configured UART bit period.

---

## 17. Required Tests

### Test 1 — Reset and Idle

Verify after reset:

```text
data_valid == 0
```

and the receiver waits normally for a frame.

---

### Test 2 — One Known Byte

Transmit:

```text
0xA7
```

Verify:

```text
data_valid == 1
data_out   == 0xA7
```

when the frame completes.

Also verify `data_valid` returns low on the next system-clock cycle.

---

### Test 3 — Known Patterns

At minimum test:

```text
0x00
0xFF
0x55
0xAA
0x01
0x80
0xA7
```

These should expose common:

- bit-order errors
- shift/index errors
- sampling errors

---

### Test 4 — Exhaustive Byte Test

Transmit every possible byte:

```text
0x00 through 0xFF
```

All 256 values must be received correctly.

---

### Test 5 — Multiple Sequential Frames

Transmit multiple valid bytes in sequence.

Verify:

- no bytes are lost
- ordering is preserved
- one `data_valid` pulse occurs per byte

---

### Test 6 — Random Idle Gaps

Insert random idle durations between UART frames.

Example:

```text
byte
idle
idle
byte
byte
idle
byte
```

The receiver must correctly return to `IDLE` and receive the next frame.

---

### Test 7 — False Start

Drive `rx` low for less than approximately half a UART bit and then return it high.

Expected result:

```text
no data_valid pulse
```

The receiver must recover and successfully receive a later valid frame.

---

### Test 8 — Invalid Stop Bit

Transmit:

```text
valid start bit
8 valid data bits
stop bit = 0
```

Expected result:

```text
no data_valid pulse
```

Afterward, return the line to idle and verify that a later valid frame is received correctly.

---

### Test 9 — Start-Phase Variation

Start frames at different offsets relative to the local system clock.

The UART start transition should not always occur exactly on `posedge clk`.

The receiver should still correctly receive the byte.

---

## 18. Waveform Inspection

Before relying only on automated tests, inspect at least one successful reception in the waveform viewer.

For a known byte such as:

```text
0xA7
```

identify:

- idle line
- start-bit transition
- start-bit midpoint sample
- each of the eight data-bit sample points
- stop-bit sample
- final `data_out`
- one-cycle `data_valid` pulse

You should be able to explain why every sampled bit corresponds to the expected byte.

---

## 19. Acceptance Criteria

`uart_rx.sv` is complete when all of the following are true:

- [ ] Module is parameterized by `CLK_FREQ` and `BAUD_RATE`
- [ ] Receiver supports 8-N-1 UART
- [ ] UART idle level is high
- [ ] Start bit is validated near its midpoint
- [ ] Data bits are sampled near their centers
- [ ] Eight data bits are received LSB first
- [ ] Stop bit is checked for logic high
- [ ] Invalid start pulses are rejected
- [ ] Invalid stop bits are rejected
- [ ] `data_out` contains the correctly reconstructed byte
- [ ] `data_valid` pulses for exactly one system-clock cycle
- [ ] All known-pattern tests pass
- [ ] All 256 possible byte values pass
- [ ] Random idle-gap tests pass
- [ ] False-start test passes
- [ ] Invalid-stop-bit test passes
- [ ] Start-phase variation tests pass
- [ ] At least one successful transaction has been manually checked in a waveform

---

## 20. Next Milestone

Do not integrate a FIFO yet.

After this specification is fully satisfied, the next milestone is:

```text
verified UART TX
       |
       | tx
       v
verified UART RX
       |
       v
cocotb scoreboard
```

That TX-to-RX loopback should be verified before FIFO integration.
