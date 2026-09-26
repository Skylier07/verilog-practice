# Verilog / SystemVerilog Practice

[![Last Commit](https://img.shields.io/github/last-commit/Skylier07/verilog-practice)](https://github.com/Skylier07/verilog-practice/commits/main)

This repository documents my journey learning **digital design, Verilog, SystemVerilog, and hardware verification with Python**. Basic practices and learning done in advance on HDLBits.

I try to practice and learn **everyday** either through this repo or HDLBits. These are the exercises, experiments, and projects I've completed while gradually building from basic combinational logic toward more complex digital systems.

**This repo is temporarily archived as I move into making my first RISC-V CPU project**
Moving to https://github.com/Skylier07/RISC-V-CPU

[![Last Commit](https://img.shields.io/github/last-commit/Skylier07/verilog-practice)](https://github.com/Skylier07/RISC-V-CPU/commits/main)

---

## Status

| Project/Excercise | Learning Objective                                                                                                                                            | Status (NEW -> OLD) |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| RX FIFO TB        | Practice end-to-end buffered verification, checking RX FIFO ordering, delayed reads, full/empty behavior, overflow handling, and UART-to-FIFO data integrity. | ✅ Done             |
| RX FIFO           | Practice multi-module control, FIFO-to-UART handshaking, FSM-based sequencing, and coordinating producer/consumer timing                                      | ✅ Done             |
| TX FIFO TB        | Practice integration verification, checking FIFO-to-UART ordering, burst traffic, and backpressure/busy behavior                                              | ✅ Done             |
| TX FIFO           | Learn multi-module control, FIFO-to-UART handshaking, FSM-based sequencing, and coordinating producer/consumer timing                                         | ✅ Done             |
| FIFO TB           | Practice stateful verification with Python Dequeue, boundary conditions, and randomized FIFO testing                                                          | ✅ Done             |
| FIFO              | Learn FIFO ordering, circular buffers, and read/write pointers                                                                                                | ✅ Done             |
| UART Loopback TB  | Practice end-to-end verification, data verification through datapth, waveform inspection                                                                      | ✅ Done             |
| RX -> RX Loopback | Practice multi-module RTL integration, and module wiring                                                                                                      | ✅ Done             |
| UART RX TB        | Learn RX verification, asynchronous timing, data_valid checking                                                                                               | ✅ Done             |
| UART RX           | Practice FSMs, serial transimission, bit sequencing, and receive handshaking                                                                                  | ✅ Done             |
| UART TX TB        | Learn FSM verification, serial bit timing, LSB-first checking, busy behavior, and randomized byte testing, separate test functions                            | ✅ Done             |
| UART TX           | Learn FSMs, serial transimission, bit sequencing, and basic handshaking                                                                                       | ✅ Done             |
| Baud-Rate Gen TB  | Practice parameterized testing with Pytest and cycle counting                                                                                                 | ✅ Done             |
| Baud-Rate Gen     | Learn parameters, $clog2, counters, and clock-enable pulses                                                                                                   | ✅ Done             |
| Shift Register TB | Practice cycle-accurate sequential verification, timing checks cocotb syntax                                                                                  | ✅ Done             |
| Shift Register    | Learn sequential logic, registers, nonblocking assignments                                                                                                    | ✅ Done             |
| ALU Test Bench    | Learn cocotb, Python models (for modules), and randomized verification                                                                                        | ✅ Done             |
| Basic ALU         | Practice combinational logic, operators, flags, and datapath design                                                                                           | ✅ Done             |

---

## What I'm Learning

- Digital logic and combinational circuits
- Verilog
- Sequential logic and finite state machines
- SystemVerilog
- Testbenches and simulation
- Python-based verification
- cocotb
- Computer architecture and RTL design

## Purpose

The goal of this repo is to keep a record of my progress while developing practical RTL design and verification skills.

I'm focusing on **writing, simulating, testing, debugging, and improving actual hardware designs**.

As I learn more, this repository will _hopefully_ continue to grow with increasingly complex designs and verification environments.

## Tools

Some of the tools used throughout this repository include:

- Verilog / SystemVerilog
- Python
- cocotb
- Icarus Verilog
- HDLBits
- Surfer
