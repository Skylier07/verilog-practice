# UART TX → RX Loopback Specification

## 1. Purpose

Create a top-level RTL module that connects the already-verified UART transmitter directly to the already-verified UART receiver.

The purpose of this module is to verify that the two independently tested blocks work correctly when integrated into one system.

This stage must contain:

```text
testbench
   ↓
UART TX
   ↓
serial wire
   ↓
UART RX
   ↓
testbench
```

Do **not** add FIFOs yet.

---

## 2. File

Create:

```text
uart_loopback.sv
```

The module should instantiate:

```text
uart_tx
uart_rx
```

Do not duplicate TX or RX logic inside the loopback module.

---

## 3. Parameters

The loopback module should expose the same UART timing parameters used by TX and RX.

```systemverilog
parameter CLK_FREQ  = 50_000_000,
parameter BAUD_RATE = 115200
```

The same parameter values must be passed into both submodules.

Conceptually:

```systemverilog
uart_tx #(
    .CLK_FREQ(CLK_FREQ),
    .BAUD_RATE(BAUD_RATE)
) ...

uart_rx #(
    .CLK_FREQ(CLK_FREQ),
    .BAUD_RATE(BAUD_RATE)
) ...
```

TX and RX must therefore operate at the same baud rate.

---

## 4. Top-Level Interface

Use an interface approximately like:

```systemverilog
module uart_loopback #(
    parameter CLK_FREQ  = 50_000_000,
    parameter BAUD_RATE = 115200
)(
    input  logic       clk,
    input  logic       reset,

    input  logic [7:0] tx_data,
    input  logic       tx_start,

    output logic       tx_busy,

    output logic [7:0] rx_data,
    output logic       rx_valid
);
```

If the existing `uart_tx.sv` or `uart_rx.sv` uses slightly different signal names, preserve the existing module interfaces and adapt the top-level names as necessary.

Do not redesign the verified TX or RX interfaces solely for this wrapper.

---

## 5. Internal Serial Connection

Declare one internal signal:

```systemverilog
logic serial_wire;
```

This signal represents the UART line between TX and RX.

The TX serial output must drive it:

```text
UART TX .tx
      │
      ▼
serial_wire
```

The RX serial input must read the exact same signal:

```text
serial_wire
      │
      ▼
UART RX .rx
```

Conceptually:

```systemverilog
uart_tx tx_inst (
    ...
    .tx(serial_wire),
    ...
);

uart_rx rx_inst (
    ...
    .rx(serial_wire),
    ...
);
```

There should be no processing or delay inserted between TX and RX.

---

## 6. Required Architecture

The completed module should behave like:

```text
                     uart_loopback

 tx_data ────────► ┌─────────┐
 tx_start ───────► │ UART TX │
                   └────┬────┘
                        │
                        │ serial_wire
                        ▼
                   ┌─────────┐
                   │ UART RX │
                   └────┬────┘
                        │
                        ├────────► rx_data
                        └────────► rx_valid

 tx_busy ◄──────── UART TX
```

Both UART modules use the same:

```text
clk
reset
CLK_FREQ
BAUD_RATE
```

---

## 7. TX Behavior

The testbench supplies:

```text
tx_data
tx_start
```

When a valid transmission request occurs, the TX must serialize the byte using the existing TX implementation.

The loopback wrapper must not modify the transmitted data.

Expected UART format remains:

```text
8-N-1
```

meaning:

```text
1 start bit
8 data bits
no parity
1 stop bit
```

Data bits are transmitted LSB first.

The serial line must idle high when the TX is inactive.

---

## 8. RX Behavior

The RX receives `serial_wire` exactly as though it were connected to an external UART transmitter.

When the RX successfully receives a full valid byte:

```text
rx_data
```

must contain the received byte and:

```text
rx_valid
```

must assert according to the existing RX contract.

For the current design, `rx_valid` should be a one-system-clock pulse.

---

## 9. End-to-End Functional Requirement

For every valid byte accepted by TX:

```text
TX input byte
```

must eventually become:

```text
RX output byte
```

without modification.

Therefore:

```text
transmitted_byte == received_byte
```

must always be true for valid completed transactions.

Example:

```text
tx_data = 8'hA7
   ↓
UART TX
   ↓
serial_wire
   ↓
UART RX
   ↓
rx_data = 8'hA7
```

---

## 10. Reset Requirements

When `reset` is asserted:

- TX must return to its existing reset state.
- RX must return to its existing reset state.
- The UART serial line should ultimately be idle high according to the TX design.
- `rx_valid` must not falsely indicate a received byte.
- No stale transaction should be treated as valid after reset.

The loopback wrapper itself should not require additional sequential reset logic unless needed solely for wrapper-owned state.

Ideally, the wrapper owns no state.

---

## 11. What the Wrapper Must NOT Contain

Do not add:

```text
FIFO
extra UART FSM
extra baud-rate generator
extra bit counter
extra RX sampling logic
extra TX serialization logic
parity
multiple stop bits
flow control
```

The wrapper's job is integration.

Most of its logic should consist of:

```text
signal declarations
module instantiations
port connections
parameter forwarding
```

---

# Verification Specification

## 12. Test 1 — Single Known Byte

First test:

```text
0xA7
```

The cocotb testbench should:

1. Reset the DUT.
2. Wait until TX can accept a transaction.
3. Set:

```text
tx_data = 0xA7
```

4. Pulse `tx_start` according to the existing TX interface.
5. Wait for the RX to assert `rx_valid`.
6. Check:

```python
assert int(dut.rx_data.value) == 0xA7
```

7. Confirm `rx_valid` returns low according to the RX specification.

Do not begin randomized testing until this test passes.

---

## 13. Waveform Inspection

For the first successful byte, inspect the waveform manually.

At minimum observe:

```text
clk
reset
tx_data
tx_start
tx_busy
serial_wire
rx_data
rx_valid
```

Verify that:

- `serial_wire` idles high.
- TX creates a low start bit.
- Data bits appear LSB first.
- A high stop bit appears.
- RX samples the same serial signal generated by TX.
- `rx_data` eventually becomes the transmitted value.
- `rx_valid` produces exactly the expected pulse.

This manual waveform inspection only needs to be done carefully for a small number of representative cases.

---

## 14. Test 2 — All 256 Byte Values

After the single-byte test passes, test every possible 8-bit value:

```python
for byte in range(256):
    ...
```

For each byte:

```text
send through TX
      ↓
wait for RX
      ↓
assert received == sent
```

Required result:

```text
0x00 → 0x00
0x01 → 0x01
...
0xFE → 0xFE
0xFF → 0xFF
```

All 256 values must pass before moving on.

---

## 15. Test 3 — Randomized Loopback

After exhaustive byte-value testing passes, send approximately:

```text
1000 random bytes
```

Use a reproducible random generator, for example:

```python
rng = random.Random(seed)
```

Keep track of transmitted and received values.

Conceptually:

```python
expected = []
received = []
```

When a byte is successfully submitted to TX:

```python
expected.append(byte)
```

When RX produces a valid byte:

```python
received.append(int(dut.rx_data.value))
```

At the end:

```python
assert received == expected
```

The ordering must be identical.

---

## 16. Random Idle Gaps

Randomized testing should include different delays between transmitted UART frames.

Traffic should not always look like:

```text
BYTE BYTE BYTE BYTE BYTE
```

It should also include patterns like:

```text
BYTE       BYTE BYTE             BYTE
```

This verifies that both modules return correctly to their idle states between transactions.

Do not violate the TX interface by starting a new transaction while TX cannot accept one.

---

## 17. Integration Debugging Rule

If:

```text
TX standalone tests pass
RX standalone tests pass
loopback test fails
```

treat the failure as an integration problem first.

Before modifying either UART FSM, check:

- TX and RX use the same `CLK_FREQ`.
- TX and RX use the same `BAUD_RATE`.
- `serial_wire` connects TX output directly to RX input.
- The TX start handshake is being used correctly.
- TX captures `tx_data` when expected.
- Reset polarity and timing agree.
- TX serial idle level is high.
- No wrapper logic is accidentally modifying the serial signal.

Use the waveform to determine which module first deviates from expected behavior.

---

# Acceptance Criteria

Part 3 is complete when all of the following are true:

```text
[ ] uart_loopback.sv exists

[ ] uart_tx is instantiated

[ ] uart_rx is instantiated

[ ] TX output connects directly to RX input through one serial_wire

[ ] TX and RX receive the same CLK_FREQ parameter

[ ] TX and RX receive the same BAUD_RATE parameter

[ ] 0xA7 loopback passes

[ ] first working transaction has been manually inspected in the waveform

[ ] all 256 possible byte values pass

[ ] approximately 1000 randomized bytes pass

[ ] random idle gaps pass

[ ] received byte order exactly matches transmitted byte order

[ ] rx_valid obeys the existing one-clock-pulse contract

[ ] no FIFO has been added yet

[ ] no loopback-specific hacks were added to uart_tx or uart_rx
```

Once every item above passes, the TX → RX integration milestone is complete.

The next milestone is standalone FIFO verification, followed by FIFO integration.
