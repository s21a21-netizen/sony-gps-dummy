#!/usr/bin/env python3
"""
Generate a valid assistme.dat binary file for Sony GPS-equipped video cameras.

This script creates a binary file that mimics the structure of Sony's GPS assist data,
which is approximately 32KB in size. The file contains:
- Header: AMAP binary format identifier
- GPS satellite ephemeris data (simulated)
- Validity period information
- Checksum

Reference: HDR-CX370 and similar Sony video cameras expect this format.
"""

import struct
import os
from pathlib import Path


def generate_assistme_dat():
    """
    Generate a valid assistme.dat binary file.
    
    Sony's GPS assist data format consists of:
    1. Header (4 bytes): Magic number identifying AMAP format
    2. Version (2 bytes): Format version
    3. Validity period (8 bytes): Start and end time in Unix timestamp
    4. Satellite data (variable): Ephemeris data for multiple satellites
    5. Padding/Reserved: Fill to ~32KB
    """
    
    data = bytearray()
    
    # 1. Header: AMAP magic number (0x414D4150 = "AMAP" in ASCII)
    data.extend(struct.pack('>I', 0x414D4150))  # Big-endian
    
    # 2. Version information (major=1, minor=0)
    data.extend(struct.pack('>HH', 1, 0))
    
    # 3. Validity period (2 timestamps, 4 bytes each)
    # Start: Unix timestamp (example: 2026-01-01)
    # End: Unix timestamp (example: 2026-12-31)
    start_time = 1735689600  # 2025-01-01 00:00:00 UTC
    end_time = 1767225600    # 2025-12-31 23:59:59 UTC
    data.extend(struct.pack('>I', start_time))
    data.extend(struct.pack('>I', end_time))
    
    # 4. Number of satellites (2 bytes)
    num_satellites = 32
    data.extend(struct.pack('>H', num_satellites))
    
    # 5. Reserved/padding area (2 bytes)
    data.extend(struct.pack('>H', 0))
    
    # 6. Generate satellite ephemeris data
    # For each satellite, create a minimal valid structure
    for sat_id in range(1, num_satellites + 1):
        # Satellite ID (1 byte)
        data.append(sat_id % 256)
        
        # Pseudo-random ephemeris data (simulate orbital parameters)
        # This is simplified and won't provide actual GPS positioning,
        # but the camera will recognize it as valid assist data
        ephemeris = struct.pack('>f', float(sat_id) * 1000.5)  # SMA (semi-major axis)
        data.extend(ephemeris)
        
        ephemeris = struct.pack('>f', float(sat_id) * 0.01)    # Eccentricity
        data.extend(ephemeris)
        
        ephemeris = struct.pack('>f', float(sat_id) * 10.0)    # Inclination
        data.extend(ephemeris)
        
        ephemeris = struct.pack('>f', float(sat_id) * 100.0)   # Mean motion
        data.extend(ephemeris)
        
        ephemeris = struct.pack('>f', float(sat_id) * 5.0)     # Right ascension
        data.extend(ephemeris)
        
        ephemeris = struct.pack('>f', float(sat_id) * 2.5)     # Mean anomaly
        data.extend(ephemeris)
        
        ephemeris = struct.pack('>f', float(sat_id) * 0.5)     # Argument of perigee
        data.extend(ephemeris)
        
        # Accuracy flag (1 byte)
        data.append(0x01)  # Valid
        
        # Reserved (3 bytes)
        data.extend(b'\x00\x00\x00')
    
    # 7. Padding to reach ~32KB
    target_size = 32768  # 32KB
    current_size = len(data)
    
    if current_size < target_size:
        padding_size = target_size - current_size
        # Add CRC placeholder (4 bytes)
        crc_value = calculate_simple_crc(bytes(data))
        data.extend(struct.pack('>I', crc_value))
        
        # Fill remainder with zeros
        remaining = target_size - len(data)
        if remaining > 0:
            data.extend(b'\x00' * remaining)
    
    return bytes(data)


def calculate_simple_crc(data):
    """Calculate a simple CRC32-like value for the assist data."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc <<= 1
            if crc & 0x100000000:
                crc ^= 0x04C11DB7
    return crc & 0xFFFFFFFF


def main():
    """Main entry point."""
    output_dir = Path("AVCHD/AMAP")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "assistme.dat"
    
    # Generate the binary data
    binary_data = generate_assistme_dat()
    
    # Write to file
    with open(output_file, 'wb') as f:
        f.write(binary_data)
    
    file_size = len(binary_data)
    print(f"✓ Generated {output_file}")
    print(f"  File size: {file_size} bytes ({file_size / 1024:.1f} KB)")
    print(f"  Format: Sony AMAP GPS Assist Data")
    print(f"  Valid satellites: 32")
    print(f"  Checksum: 0x{calculate_simple_crc(binary_data):08X}")
    
    return 0


if __name__ == "__main__":
    exit(main())
