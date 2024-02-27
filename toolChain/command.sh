#!/bin/bash

# URL of the file to download
URL="https://github.com/stnolting/riscv-gcc-prebuilt/releases/download/rv32e-231223/riscv32-unknown-elf.gcc-rve-13.2.0.tar.gz"

# Download the file
wget "$URL" || { echo "Failed to download file"; exit 1; }

# Extract the downloaded file in the same directory as the script
tar -xvf riscv32-unknown-elf.gcc-rve-13.2.0.tar.gz || { echo "Failed to extract file"; exit 1; }

# Clean up the downloaded tar.gz file
rm riscv32-unknown-elf.gcc-rve-13.2.0.tar.gz

echo "Extraction completed successfully."
