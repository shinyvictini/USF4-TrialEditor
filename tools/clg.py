
import struct
from pathlib import Path
from moves import RYX_MOVES


class CLGFile:

    LEVEL_SIZE = 0x70
    COMMAND_SIZE = 0x108

    def __init__(self, path):
        self.data = bytearray(Path(path).read_bytes())
        self.original_data = bytes(self.data)

        if self.data[:4] != b"#CLG":
            raise ValueError("Invalid CLG file")

        self.trial_count = self.u32(0x30)
        self.level_table = self.u32(0x34)

    def u16(self, offset):
        return struct.unpack_from("<H", self.data, offset)[0]

    def u32(self, offset):
        return struct.unpack_from("<I", self.data, offset)[0]

    def string(self, offset, length=32):
        raw = self.data[offset:offset + length]
        return raw.split(b"\x00")[0].decode(
            "ascii", errors="replace"
        )

    def get_trial(self, number):

        if not 1 <= number <= self.trial_count:
            raise ValueError("Invalid trial number")

        level = self.level_table + (number - 1) * self.LEVEL_SIZE

        table = level + self.u32(level + 0x6C)

        return {
            "number": number,
            "name": self.string(level),
            "condition_flag": self.u32(table),
            "command_count": self.u32(table + 8),
            "command_start": table + self.u32(table + 12)
        }

    def get_command(self, trial_number, move_number):

        trial = self.get_trial(trial_number)

        if not 1 <= move_number <= trial["command_count"]:
            raise ValueError("Invalid move number")

        offset = (
            trial["command_start"]
            + (move_number - 1) * self.COMMAND_SIZE
        )

        strings = []

        for i in range(8):
            value = self.string(offset + i * 0x20)

            if value:
                strings.append(value)

        return {
            "offset": offset,
            "strings": strings,
            "criteria_count": self.u16(offset + 0x102),
            "relative_reference": self.u32(offset + 0x104)
        }

    def replace_command(
        self,
        target_trial,
        target_move,
        source_trial,
        source_move
    ):

        source = self.get_command(
            source_trial, source_move
        )["offset"]

        destination = self.get_command(
            target_trial, target_move
        )["offset"]

        record = bytearray(
            self.original_data[
                source:source + self.COMMAND_SIZE
            ]
        )

        relative = struct.unpack_from(
            "<I", record, 0x104
        )[0]

        new_relative = relative + source - destination

        struct.pack_into(
            "<I", record, 0x104, new_relative
        )

        self.data[
            destination:destination + self.COMMAND_SIZE
        ] = record

    def set_move(self, trial, position, move_name):

        if move_name not in RYX_MOVES:
            raise ValueError(f"Unknown move: {move_name}")

        source_trial, source_move = RYX_MOVES[move_name]

        self.replace_command(
            trial,
            position,
            source_trial,
            source_move
        )
    def redirect_trial(self, trial, source_trial, count):

        source = self.get_trial(source_trial)

        if not 1 <= count <= source["command_count"]:
            raise ValueError("Insufficient command slots")

        level = (
            self.level_table
            + (trial - 1) * self.LEVEL_SIZE
        )

        table = level + self.u32(level + 0x6C)

        new_relative = source["command_start"] - table

        # Update command count
        struct.pack_into(
            "<I", self.data, table + 8, count
        )

        # Update command block reference
        struct.pack_into(
            "<I", self.data, table + 12, new_relative
        )

        print(
            f"Trial {trial} redirected to "
            f"Trial {source_trial}'s command block"
        )
    def set_command_count(self, trial, count):

        original_count = self.get_trial(trial)["command_count"]

        if not 1 <= count <= original_count:
            raise ValueError("Invalid command count")

        level = (
            self.level_table
            + (trial - 1) * self.LEVEL_SIZE
        )

        table = level + self.u32(level + 0x6C)

        struct.pack_into(
            "<I", self.data, table + 8, count
        )

        print(f"Trial {trial}: {original_count} -> {count} moves")

    def set_combo(self, trial, moves):

        existing_count = self.get_trial(trial)["command_count"]

        if len(moves) != existing_count:
            raise ValueError(
                f"Trial {trial} currently requires "
                f"{existing_count} moves"
            )

        for move in moves:
            if move not in RYX_MOVES:
                raise ValueError(f"Unknown move: {move}")

        for position, move in enumerate(moves, start=1):
            self.set_move(trial, position, move)

        print(f"Trial {trial}: {' -> '.join(moves)}")

    def save(self, path):

        Path(path).write_bytes(self.data)

        print(f"Saved CLG: {path}")

    def print_trials(self):

        for number in range(1, self.trial_count + 1):

            trial = self.get_trial(number)

            print(
                f"\nTrial {number} | "
                f"Moves: {trial['command_count']} | "
                f"Flag: {trial['condition_flag']}"
            )

            for move in range(1, trial["command_count"] + 1):

                command = self.get_command(number, move)

                print(
                    f"  Move {move} | "
                    f"0x{command['offset']:04X} | "
                    f"{', '.join(command['strings'])}"
                )


if __name__ == "__main__":

    clg = CLGFile(
        r"D:\USF4-TrialEditor\originals\RYX_swan.clg"
    )

    clg.redirect_trial(1, 24, 3)

    clg.set_combo(1, [
        "st_hp",
        "lk_tatsu",
        "hp_shoryuken"
    ])

    clg.save(
        r"D:\USF4-TrialEditor\working\RYX_swan.clg"
    )