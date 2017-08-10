import base64
import gzip
import json
import tempfile
from typing import Callable

import sc2reader
import techlabreactor
from aiohttp.web_exceptions import HTTPFound
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from .chart import make_chart_data

CHUNK_SIZE = 1024


def _compress_and_encode(data: str) -> str:
    compressed = gzip.compress(data.encode())
    return base64.b64encode(compressed).decode()


class ReplayAnalyser:

    def __init__(self, redirect_supplier: Callable[[str], str]):
        self.redirect_supplier = redirect_supplier

    async def analyse_replay(self, request: Request) -> Response:

        if request.content_type.startswith("multipart/"):
            reader = await request.multipart()
            replay_data = await reader.next()
            replay_name = replay_data.filename
        else:
            replay_name = ""
            replay_data = request.content

        if replay_data is None:
            return Response(body="Invalid Replay", status=402)

        with tempfile.TemporaryFile() as replay_file:
            while True:
                chunk = await request.content.read(CHUNK_SIZE)
                if not chunk:
                    break

                replay_file.write(chunk)

            replay_file.seek(0)

            try:
                replay = sc2reader.load_replay(replay_file)

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

            except Exception as e:
                return Response(body="Invalid Replay\n" + str(e), status=402)

        param = _compress_and_encode(json.dumps(data))
        return HTTPFound(self.redirect_supplier(param))
