from typing import IO, Tuple

# noinspection PyUnresolvedReferences
import sc2reader
import techlabreactor


def make_chart_data(inject_states: list, fps: float) -> list:
    return [
        [
            {"x": int((frame * 1000) / (1.4 * fps)), "y": (offset * 10) + (9 if state else 0)}
            for frame, state
            in states
            ]
        for offset, states
        in enumerate(inject_states)]


def analyse_replay_file(replay_name: str, replay_file: IO[bytes]) -> Tuple[str, dict]:
    replay = sc2reader.SC2Reader().load_replay(replay_file)

    data = {
        "players": [],
        "replayName": replay_name
    }

    for player in replay.players:
        inject_states = techlabreactor.get_hatchery_inject_states_for_player(player, replay)

        if not inject_states:
            continue

        chart_data = make_chart_data(inject_states, replay.game_fps)

        overall_inject_efficiency = techlabreactor.calculate_overall_inject_efficiency(inject_states)
        overall_inject_efficiency_str = "{0:.2f}".format(overall_inject_efficiency * 100)

        inject_efficiency_from_first_queen_completed = techlabreactor.calculate_inject_efficiency_from_frame(
            techlabreactor.find_first_queen_completed_frame_for_player(player, replay),
            inject_states)
        inject_efficiency_from_first_queen_completed_str = "{0:.2f}".format(
            inject_efficiency_from_first_queen_completed * 100)

        inject_pops = techlabreactor.get_inject_pops_for_player(player, replay)

        data["players"].append({
            "chartData": chart_data,
            "overallInjectEfficiency": overall_inject_efficiency_str,
            "injectEfficiencyFromFirstQueenCompleted": inject_efficiency_from_first_queen_completed_str,
            "playerName": player.name,
            "injectPops": inject_pops
        })

    return replay.filehash, data
