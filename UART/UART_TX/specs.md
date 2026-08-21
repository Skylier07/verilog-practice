# UART Transmitter Specification

## Module

```systemverilog
module uart_tx(
    input  logic       clk,
    input  logic       reset,
    input  logic       baud_tick,
    input  logic       start,
    input  logic [7:0] data_in,
    output logic       tx,
    output logic       busy
);
```

## UART Format

Transmit one byte using:

```text
Idle → Start → 8 Data Bits → Stop → Idle
  1      0       LSB first      1      1
```

- Idle line: `tx = 1`
- Start bit: `tx = 0`
- Data bits: 8 bits, LSB first
- Stop bit: `tx = 1`
- Each transmitted bit lasts one `baud_tick` period.

## FSM

Use four states:

```systemverilog
typedef enum logic [1:0] {
    IDLE,
    START,
    DATA,
    STOP
} state_t;
```

Required transitions:

```text
IDLE --start--> START
START --baud_tick--> DATA
DATA --baud_tick after bit 7--> STOP
STOP --baud_tick--> IDLE
```

## Required Behavior

### Reset

On synchronous reset:

```text
state = IDLE
tx    = 1
busy  = 0
```

### IDLE

```text
tx   = 1
busy = 0
```

If `start == 1`:

- Capture `data_in` into an internal register.
- Set `busy = 1`.
- Begin transmission.

### START

```text
tx = 0
busy = 1
```

Hold the start bit until the next `baud_tick`.

### DATA

- Transmit the captured byte from bit `0` through bit `7`.
- Send one bit per baud period.
- Advance the bit index only on `baud_tick`.
- Keep `busy = 1`.

### STOP

```text
tx   = 1
busy = 1
```

Hold the stop bit for one baud period, then return to `IDLE`.

## Input Handling

- Accept a new `start` request only while idle.
- Changes to `data_in` after transmission begins must not affect the current byte.
- Ignore new `start` requests while `busy == 1`.

## Suggested Internal State

```text
state
data_reg[7:0]
bit_index
```

## Acceptance Criteria

The module is complete when it correctly:

- Idles with `tx = 1`.
- Sends one start bit.
- Sends exactly 8 data bits LSB first.
- Sends one stop bit.
- Advances UART timing only on `baud_tick`.
- Keeps each bit active for one baud period.
- Captures `data_in` when transmission begins.
- Asserts `busy` for the full transmission.
- Ignores new requests while busy.
- Returns to idle after transmission.
- Returns to idle on reset.
