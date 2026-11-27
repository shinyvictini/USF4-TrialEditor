
import struct
from pathlib import Path
from clg import CLGFile
from moves import RYX_MOVES, RYX_CUSTOM_MOVES


class CLGBuilder:

    def __init__(self, path):

        self.original = CLGFile(path)
        self.combos = {}
        self.ultras = {}
        self.stances = {}

        self.command_start = self.original.get_trial(
            1
        )["command_start"]

        last = self.original.get_trial(
            self.original.trial_count
        )

        self.command_end = (
            last["command_start"]
            + last["command_count"] * CLGFile.COMMAND_SIZE
        )

        for trial in range(1, self.original.trial_count + 1):

            self.reset_trial(trial)

    def reset_trial(self, trial):

        count = self.original.get_trial(
            trial
        )["command_count"]

        self.combos[trial] = [
            (trial, move)
            for move in range(1, count + 1)
        ]
        level = (
        self.original.level_table
        + (trial - 1) * CLGFile.LEVEL_SIZE
        )

        table_b = level + self.original.u32(level + 0x6C)

        self.ultras[trial] = self.original.u32(level + 0x54)
        self.stances[trial] = self.original.u32(table_b)

    def set_combo(self, trial, moves):

        if trial not in self.combos:
            raise ValueError("Invalid trial")

        if not moves:
            raise ValueError("Combo cannot be empty")

        combo = []

        for move in moves:

            if move in RYX_CUSTOM_MOVES:
                combo.append(RYX_CUSTOM_MOVES[move])

            elif move in RYX_MOVES:
                combo.append(RYX_MOVES[move])

            else:
                raise ValueError(f"Unknown move: {move}")

        self.combos[trial] = combo

    def build(self):

        original = self.original.data
        command_size = CLGFile.COMMAND_SIZE

        total_commands = sum(
            len(combo)
            for combo in self.combos.values()
        )

        old_size = self.command_end - self.command_start
        new_size = total_commands * command_size
        size_change = new_size - old_size

        new_command_end = self.command_start + new_size

        # Preserve header and tables
        result = bytearray(
            original[:self.command_start]
        )

        # Preserve original action data
        criteria = bytearray(
            original[self.command_end:]
        )

        for trial, combo in self.combos.items():

            level = (
                self.original.level_table
                + (trial - 1) * CLGFile.LEVEL_SIZE
            )

            table = (
                level
                + self.original.u32(level + 0x6C)
            )
            struct.pack_into(
                "<I", result, level + 0x54, self.ultras[trial]
            )

            struct.pack_into(
                "<I", result, table, self.stances[trial]
            )

            # Update trial count and command reference
            struct.pack_into(
                "<II",
                result,
                table + 8,
                len(combo),
                len(result) - table
            )

            for move in combo:

                custom = isinstance(move, dict)

                if custom:
                    source_trial, source_move = move["template"]
                else:
                    source_trial, source_move = move

                source = self.original.get_command(
                    source_trial, source_move
                )["offset"]

                destination = len(result)

                record = bytearray(
                    original[source:source + command_size]
                )

                if custom:

                    # Clear all eight text slots
                    record[:0x100] = bytes(0x100)

                    # Write custom text identifiers
                    for i, text in enumerate(move["strings"]):

                        encoded = text.encode("ascii")

                        if i >= 8 or len(encoded) >= 32:
                            raise ValueError("Invalid text identifier")

                        start = i * 0x20

                        record[start:start + len(encoded)] = encoded

                    action_ids = move["action_ids"]

                    if not action_ids:
                        raise ValueError("Empty action list")

                    # Allocate new action data
                    target = new_command_end + len(criteria)

                    for action_id in action_ids:

                        criteria.extend(
                            struct.pack("<I", action_id)
                        )

                    # Set criteria count
                    struct.pack_into(
                        "<H", record, 0x102,
                        len(action_ids)
                    )

                    new_relative = target - destination

                else:

                    # Relocate original action reference
                    relative = struct.unpack_from(
                        "<I", record, 0x104
                    )[0]

                    new_relative = (
                        relative
                        + source
                        - destination
                        + size_change
                    )

                struct.pack_into(
                    "<I", record, 0x104,
                    new_relative
                )

                result.extend(record)

        # Append original and custom action data
        result.extend(criteria)

        print(f"Total commands: {total_commands}")
        print(f"Command size change: {size_change:+} bytes")
        print(f"Criteria size: {len(criteria)} bytes")
        print(f"Original size: {len(original)} bytes")
        print(f"New size: {len(result)} bytes")

        return result

    def save(self, path):

        Path(path).write_bytes(self.build())

        print(f"Saved: {path}")


if __name__ == "__main__":

    builder = CLGBuilder(
        r"D:\USF4-TrialEditor\originals\RYX_swan.clg"
    )

    # Ensure original reconstruction still works
    assert builder.build() == builder.original.data

    print("\nRound-trip successful!\n")

    # Experimental move tests
    builder.set_combo(1, ["lp_hadoken"])
    builder.set_combo(2, ["mp_hadoken"])
    builder.set_combo(3, ["hp_hadoken"])
    builder.set_combo(4, ["ex_hadoken"])
    builder.set_combo(5, ["mp_shoryuken"])
    builder.set_combo(6, ["mk_tatsu"])
    builder.set_combo(7, ["lk_ryusokyaku"])

    builder.save(
        r"D:\USF4-TrialEditor\working\RYX_swan.clg"
    )
