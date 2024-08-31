# cython: language_level=3

from libcpp cimport bool

cdef class GameStateCy:
    cdef public tuple player_hands
    cdef public int current_player
    cdef public int left_end
    cdef public int right_end
    cdef public int consecutive_passes

    def __init__(self, tuple player_hands, int current_player, int left_end, int right_end, int consecutive_passes):
        self.player_hands = player_hands
        self.current_player = current_player
        self.left_end = left_end
        self.right_end = right_end
        self.consecutive_passes = consecutive_passes

    cpdef bool is_game_over(self):
        cdef int i
        for i in range(4):
            if len(self.player_hands[i]) == 0:
                return True
        return self.consecutive_passes == 4

    @staticmethod
    def static_is_game_over(tuple player_hands, int consecutive_passes):
        cdef int i
        for i in range(4):
            if len(player_hands[i]) == 0:
                return True
        return consecutive_passes == 4