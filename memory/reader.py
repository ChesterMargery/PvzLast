"""
Memory Reader Module
Handles reading values from PVZ process memory
"""

import ctypes
from typing import Optional, List
from data.offsets import Offset


class MemoryReader:
    """Reads values from process memory"""
    
    def __init__(self, kernel32, process_handle: int):
        self.kernel32 = kernel32
        self.process = process_handle
        
    def read_int(self, address: int) -> int:
        """Read a 4-byte integer from memory"""
        buf = ctypes.c_int()
        self.kernel32.ReadProcessMemory(
            self.process, address, ctypes.byref(buf), 4, None
        )
        return buf.value
    
    def read_uint(self, address: int) -> int:
        """Read a 4-byte unsigned integer from memory"""
        buf = ctypes.c_uint()
        self.kernel32.ReadProcessMemory(
            self.process, address, ctypes.byref(buf), 4, None
        )
        return buf.value
    
    def read_float(self, address: int) -> float:
        """Read a 4-byte float from memory"""
        buf = ctypes.c_float()
        self.kernel32.ReadProcessMemory(
            self.process, address, ctypes.byref(buf), 4, None
        )
        return buf.value
    
    def read_byte(self, address: int) -> int:
        """Read a single byte from memory"""
        buf = ctypes.c_byte()
        self.kernel32.ReadProcessMemory(
            self.process, address, ctypes.byref(buf), 1, None
        )
        return buf.value
    
    def read_bool(self, address: int) -> bool:
        """Read a boolean (single byte) from memory"""
        return self.read_byte(address) != 0
    
    def read_bytes(self, address: int, size: int) -> bytes:
        """Read multiple bytes from memory"""
        buf = (ctypes.c_byte * size)()
        self.kernel32.ReadProcessMemory(
            self.process, address, ctypes.byref(buf), size, None
        )
        return bytes(buf)
    
    def read_short(self, address: int) -> int:
        """Read a 2-byte short from memory"""
        buf = ctypes.c_short()
        self.kernel32.ReadProcessMemory(
            self.process, address, ctypes.byref(buf), 2, None
        )
        return buf.value
    
    def read_double(self, address: int) -> float:
        """Read an 8-byte double from memory"""
        buf = ctypes.c_double()
        self.kernel32.ReadProcessMemory(
            self.process, address, ctypes.byref(buf), 8, None
        )
        return buf.value
    
    # ========================================================================
    # PVZ Specific Reading Methods
    # ========================================================================
    
    def get_pvz_base(self) -> int:
        """Get the PVZ base pointer"""
        return self.read_int(Offset.BASE)
    
    def get_board(self) -> int:
        """Get the Board/MainObject pointer"""
        base = self.get_pvz_base()
        if base == 0:
            return 0
        return self.read_int(base + Offset.MAIN_OBJECT)
    
    def get_game_ui(self) -> int:
        """Get the current game UI state"""
        base = self.get_pvz_base()
        if base == 0:
            return 0
        return self.read_int(base + Offset.GAME_UI)
    
    def is_in_game(self) -> bool:
        """Check if player is currently in a game"""
        return self.get_game_ui() == 3
    
    def get_sun(self) -> int:
        """Get current sun amount"""
        board = self.get_board()
        if board == 0:
            return 0
        return self.read_int(board + Offset.SUN)
    
    def get_wave(self) -> int:
        """Get current wave number"""
        board = self.get_board()
        if board == 0:
            return 0
        return self.read_int(board + Offset.WAVE)
    
    def get_total_waves(self) -> int:
        """Get total number of waves"""
        board = self.get_board()
        if board == 0:
            return 0
        return self.read_int(board + Offset.TOTAL_WAVE)
    
    def get_game_clock(self) -> int:
        """Get game clock (time in cs)"""
        board = self.get_board()
        if board == 0:
            return 0
        return self.read_int(board + Offset.GAME_CLOCK)
    
    def get_scene(self) -> int:
        """Get current scene type"""
        board = self.get_board()
        if board == 0:
            return 0
        return self.read_int(board + Offset.SCENE)
    
    def get_zombie_array(self) -> int:
        """Get zombie array base address"""
        board = self.get_board()
        if board == 0:
            return 0
        return self.read_int(board + Offset.ZOMBIE_ARRAY)
    
    def get_zombie_count_max(self) -> int:
        """Get maximum zombie count (array size)"""
        board = self.get_board()
        if board == 0:
            return 0
        return self.read_int(board + Offset.ZOMBIE_COUNT_MAX)
    
    def get_plant_array(self) -> int:
        """Get plant array base address"""
        board = self.get_board()
        if board == 0:
            return 0
        return self.read_int(board + Offset.PLANT_ARRAY)
    
    def get_plant_count_max(self) -> int:
        """Get maximum plant count (array size)"""
        board = self.get_board()
        if board == 0:
            return 0
        return self.read_int(board + Offset.PLANT_COUNT_MAX)
    
    def get_seed_array(self) -> int:
        """Get seed/card array base address"""
        board = self.get_board()
        if board == 0:
            return 0
        return self.read_int(board + Offset.SEED_ARRAY)
    
    def get_item_array(self) -> int:
        """Get item/collectible array base address"""
        board = self.get_board()
        if board == 0:
            return 0
        return self.read_int(board + Offset.ITEM_ARRAY)
    
    def get_item_count_max(self) -> int:
        """Get maximum item count (array size)"""
        board = self.get_board()
        if board == 0:
            return 0
        return self.read_int(board + Offset.ITEM_COUNT_MAX)
