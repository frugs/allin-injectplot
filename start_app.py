import aiohttp.web
import pkg_resources

import injects


class App(aiohttp.web.Application):

    def __init__(self):
        super().__init__()

        replay_analyser = injects.ReplayAnalyser(lambda x: "analysis.html?data={}".format(x))

        self.router.add_post("/upload", replay_analyser.analyse_replay)
        self.router.add_static('/', pkg_resources.resource_filename(__name__, "public"))


def main():
    aiohttp.web.run_app(App(), port=32433)
    pass


if __name__ == "__main__":
    main()