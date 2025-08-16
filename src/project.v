/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */
`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (1=output)
    input  wire       ena,      // goes high when design is selected
    input  wire       clk,      // clock
    input  wire       rst_n     // active-low reset
`ifdef GL_TEST
  , input  wire       VPWR,     // for gate-level sims
    input  wire       VGND
`endif
);

  // Instantiate your actual design (pass TT harness straight through)
  tt_um_mult8_shiftadd #(.FRAC_BITS(0)) u_mult (
      .ui_in  (ui_in),
      .uo_out (uo_out),
      .uio_in (uio_in),
      .uio_out(uio_out),
      .uio_oe (uio_oe),
      .ena    (ena),
      .clk    (clk),
      .rst_n  (rst_n)
  );

endmodule
