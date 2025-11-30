"""
ASM Injector Module
Handles shellcode injection for calling game functions directly
"""

import struct
import ctypes
from ctypes import wintypes
from typing import Optional, List

from data.offsets import Offset
from memory.reader import MemoryReader


# Windows API constants
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
MEM_RELEASE = 0x8000
PAGE_EXECUTE_READWRITE = 0x40


class AsmInjector:
    """
    Injects and executes ASM shellcode in the game process
    
    This allows direct calling of game functions for reliable operations
    like planting, shoveling, and firing cob cannons.
    """
    
    def __init__(self, kernel32, process_handle: int, reader: MemoryReader):
        self.kernel32 = kernel32
        self.process = process_handle
        self.reader = reader
    
    def alloc_memory(self, size: int) -> int:
        """
        Allocate executable memory in the game process
        
        Args:
            size: Number of bytes to allocate
            
        Returns:
            Address of allocated memory, or 0 on failure
        """
        addr = self.kernel32.VirtualAllocEx(
            self.process,
            None,
            size,
            MEM_COMMIT | MEM_RESERVE,
            PAGE_EXECUTE_READWRITE
        )
        return addr or 0
    
    def free_memory(self, address: int):
        """Free previously allocated memory"""
        self.kernel32.VirtualFreeEx(self.process, address, 0, MEM_RELEASE)
    
    def write_bytes(self, address: int, data: bytes) -> bool:
        """Write bytes to process memory"""
        written = ctypes.c_size_t()
        return self.kernel32.WriteProcessMemory(
            self.process, address, data, len(data), ctypes.byref(written)
        )
    
    def execute_shellcode(self, shellcode: bytes, timeout: int = 1000) -> bool:
        """
        Execute shellcode in the game process
        
        Process:
        1. Allocate executable memory in game process
        2. Write shellcode to that memory
        3. Create remote thread to execute it
        4. Wait for completion
        5. Free memory
        
        Args:
            shellcode: The machine code to execute
            timeout: Maximum time to wait for execution (ms)
            
        Returns:
            True if execution succeeded, False otherwise
        """
        # Allocate memory for shellcode
        addr = self.alloc_memory(len(shellcode) + 16)
        if not addr:
            return False
        
        try:
            # Write shellcode to game memory
            if not self.write_bytes(addr, shellcode):
                return False
            
            # Create remote thread to execute
            thread_id = wintypes.DWORD()
            thread = self.kernel32.CreateRemoteThread(
                self.process,
                None, 0,
                addr, None, 0,
                ctypes.byref(thread_id)
            )
            
            if not thread:
                return False
            
            # Wait for thread to complete
            self.kernel32.WaitForSingleObject(thread, timeout)
            self.kernel32.CloseHandle(thread)
            return True
            
        finally:
            # Always free the allocated memory
            self.free_memory(addr)
    
    # ========================================================================
    # High-Level Game Functions
    # ========================================================================
    
    def plant(self, row: int, col: int, plant_type: int, imitator_type: int = -1) -> bool:
        """
        Plant at a specific position
        
        Calls the game's plant function at 0x0040D120 directly.
        
        Calling convention (from pvz_cpp_bot/dllmain.cpp):
            push imitatorType  (-1 = not imitator)
            push plantType
            mov eax, row
            push col
            mov edi, pBoard
            push edi
            call 0x0040D120
        
        Args:
            row: Row to plant (0-5)
            col: Column to plant (0-8)
            plant_type: Plant type ID
            imitator_type: Type if using imitator (-1 if not)
            
        Returns:
            True if successful, False otherwise
        """
        board = self.reader.get_board()
        if board == 0:
            return False
        
        shellcode = bytes([
            # push imitator_type
            0x68, *struct.pack('<i', imitator_type),
            
            # push plant_type
            0x68, *struct.pack('<i', plant_type),
            
            # mov eax, row
            0xB8, *struct.pack('<I', row),
            
            # push col
            0x68, *struct.pack('<i', col),
            
            # mov edi, board
            0xBF, *struct.pack('<I', board),
            
            # push edi (board)
            0x57,
            
            # mov edx, FUNC_PLANT
            0xBA, *struct.pack('<I', Offset.FUNC_PLANT),
            
            # call edx
            0xFF, 0xD2,
            
            # ret
            0xC3
        ])
        
        return self.execute_shellcode(shellcode)
    
    def shovel(self, row: int, col: int) -> bool:
        """
        Remove/shovel a plant at a specific position
        
        First finds the plant at the position, then calls RemovePlant.
        
        Args:
            row: Row of plant
            col: Column of plant
            
        Returns:
            True if successful, False otherwise
        """
        board = self.reader.get_board()
        if board == 0:
            return False
        
        # Find the plant at this position
        plant_array = self.reader.read_int(board + Offset.PLANT_ARRAY)
        if plant_array == 0:
            return False
            
        plant_max = self.reader.read_int(board + Offset.PLANT_COUNT_MAX)
        if plant_max <= 0 or plant_max > 200:
            return False
        
        plant_addr = None
        for i in range(plant_max):
            addr = plant_array + i * Offset.PLANT_SIZE
            if self.reader.read_byte(addr + Offset.P_DEAD):
                continue
            p_row = self.reader.read_int(addr + Offset.P_ROW)
            p_col = self.reader.read_int(addr + Offset.P_COL)
            if p_row == row and p_col == col:
                plant_addr = addr
                break
        
        if plant_addr is None:
            return False
        
        # Call RemovePlant
        shellcode = bytes([
            # push plant_addr
            0x68, *struct.pack('<I', plant_addr),
            
            # mov edx, FUNC_REMOVE_PLANT
            0xBA, *struct.pack('<I', Offset.FUNC_REMOVE_PLANT),
            
            # call edx
            0xFF, 0xD2,
            
            # ret
            0xC3
        ])
        
        return self.execute_shellcode(shellcode)
    
    def refresh_seed_cooldowns(self) -> bool:
        """
        Refresh all seed card cooldowns
        
        Returns:
            True if successful, False otherwise
        """
        board = self.reader.get_board()
        if board == 0:
            return False
        
        seed_bank = self.reader.read_int(board + Offset.SEED_ARRAY)
        if seed_bank == 0:
            return False
        
        shellcode = bytes([
            # push seed_bank
            0x68, *struct.pack('<I', seed_bank),
            
            # mov eax, FUNC_REFRESH_SEEDS
            0xB8, *struct.pack('<I', Offset.FUNC_REFRESH_SEEDS),
            
            # call eax
            0xFF, 0xD0,
            
            # ret
            0xC3
        ])
        
        return self.execute_shellcode(shellcode)
    
    def fire_cob(self, cob_index: int, target_x: float, target_y: float) -> bool:
        """
        Fire a cob cannon at a specific position
        
        Note: Not yet implemented. The cob cannon firing requires more complex
        shellcode that varies by game version. See AVZ cob_manager for reference.
        
        TODO: Implement proper cob firing shellcode based on AVZ cob_manager.cpp
        
        Args:
            cob_index: Index of the cob cannon plant
            target_x: Target x coordinate
            target_y: Target y coordinate
            
        Returns:
            True if successful, False otherwise (currently always False)
        """
        # This is a placeholder - actual implementation requires:
        # 1. Finding the cob cannon plant
        # 2. Setting up mouse cursor position
        # 3. Calling the game's cob fire function
        # Reference: AVZ src/avz_cob_manager.cpp
        return False
    
    def collect_sun(self, item_addr: int) -> bool:
        """
        Collect a specific sun/item
        
        This is a simple method that sets the collected flag.
        The game will automatically add the sun value.
        
        Args:
            item_addr: Memory address of the item
            
        Returns:
            True if successful
        """
        # Write directly to the collected flag
        buf = ctypes.c_byte(1)
        return self.kernel32.WriteProcessMemory(
            self.process, 
            item_addr + Offset.I_COLLECTED, 
            ctypes.byref(buf), 
            1, 
            None
        )
