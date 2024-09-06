`default_nettype none
`timescale 1ns / 1ps

// A processing element (PE) module that performs a multiply and accumulate operation.
// A temporal dataflow is used where accumulation occurs over multiple clock cycles.
// We use a weight stationary dataflow where the weight can be stored in the reg file for reuse

module pe #(
    // Parameters for data precision and size of local register file
    parameter IN_PRECISION = 16,
    parameter OUT_PRECISION = 32,      // must be >= IN_PRECISION
    parameter REG_SIZE = 4
) (
    input wire clk,                    // Clock signal
    input wire rst,                    // Reset signal

    input wire [IN_PRECISION-1:0] act, // Input activation
    input wire [IN_PRECISION-1:0] wgt, // Input weight

    input wire store,                  // Store the weight in the reg file
    input wire reuse,                  // Reuse the weight in the reg file
    input wire [REG_SIZE-1:0] addr,    // Address to read/write from reg file
    
    input wire update_out,             // End of current dot product, send output
    output reg [OUT_PRECISION-1:0] out // Output data
);

    // Init local register file. Reserve first reg for temporal accumulation
    reg [OUT_PRECISION-1:0] regfile [REG_SIZE-1:0];

    // Local flag to reset the accumulation in the regfile, not add on
    reg start_new_dot_product; 
    
    // Internal behaviour: multiply act * weight and accumulate into regfile
    always @(posedge clk) begin
        // State A: Resetting
        if (rst) begin
            // Empty the register file
            for (int i=0; i<REG_SIZE; i=i+1) begin
                regfile[i] <= 0;
            end

            // Reset the output
            out <= 0;
            start_new_dot_product <= 0;
        end 
        
        // State B: MAC operation
        else begin
            // Store the weight in the reg file
            if (store) begin
                regfile[addr] <= wgt;
            end 

            // Multiply and accumulate starting from 0 accumulated
            if (start_new_dot_product) begin
                if (reuse) begin                                // with regfile
                    // try a pipelined multiplier here to reduce critical path
                    regfile[0] <= act * regfile[addr];
                end else begin                                  // with new input
                    regfile[0] <= act * wgt;    
                end
                
                start_new_dot_product <= 0;
            end 

            // multiply and accumulate starting with existing accumulation
            else begin
                if (reuse) begin                                    // with regfile
                    regfile[0] <= regfile[0] + act * regfile[addr];
                end else begin                                      // with new input
                    regfile[0] <= regfile[0] + act * wgt;
                end
            end

            // If we are at the end of the dot product, send the output
            if (update_out) begin
                out <= regfile[0];
                start_new_dot_product <= 1; // prep for next dot product next cycle
            end
        end
    end

endmodule