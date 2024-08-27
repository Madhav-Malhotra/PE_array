`default_nettype none
`timescale 1ns / 1ps

// A processing element (PE) module that performs a multiply and accumulate operation.
// A temporal dataflow is used where accumulation occurs over multiple clock cycles.
// We use a weight stationary dataflow where the weight can be stored in the reg file for reuse

module pe #(
    // Parameters for data precision and size of local register file
    parameter IN_PRECISION = 16,
    parameter OUT_PRECISION = 16,      // must be >= IN_PRECISION
    parameter REG_SIZE = 4
) (
    input wire clk,                    // Clock signal
    input wire rst,                    // Reset signal

    input wire [IN_PRECISION-1:0] act, // Input activation
    input wire [IN_PRECISION-1:0] wgt, // Input weight

    input wire store,                  // Store the weight in the reg file
    input wire reuse,                  // Reuse the weight in the reg file
    input wire [REG_SIZE-1:0] addr,    // Address to read/write from reg file
    
    input wire finish,                 // End of current dot product, send output
    output reg [OUT_PRECISION-1:0] out // Output data
);

    // Init local register file. Reserve first reg for temporal accumulation
    reg [OUT_PRECISION-1:0] regfile [REG_SIZE-1:0];
    
    // Internal behaviour: multiply act * weight and accumulate into regfile
    always @(posedge clk) begin
        if (rst) begin
            // Empty the register file
            for (int i=0; i<REG_SIZE; i=i+1) begin
                regfile[i] <= 0;
            end

            // Reset the output
            out <= 0;
        end else begin
            // Store the weight in the reg file
            if (store) begin
                regfile[addr] <= wgt;
            end 

            // Multiply and accumulate 
            if (reuse) begin                                    // with regfile
                regfile[0] <= regfile[0] + act * regfile[addr];
            end else begin                                      // with new input
                regfile[0] <= regfile[0] + act * wgt;
            end

            // If we are at the end of the dot product, send the output
            if (finish) begin
                out <= regfile[0];
                regfile[0] <= 0; // prep for next dot product
            end
        end
    end

endmodule