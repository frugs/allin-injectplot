def make_chart_data(inject_states: list, fps: float) -> list:
    return [
        [
            {"x": int((frame * 1000) / (1.4 * fps)), "y": (offset * 10) + (9 if state else 0)}
            for frame, state
            in states
            ]
        for offset, states
        in enumerate(inject_states)]
