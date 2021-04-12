import json
from typing import List

from mk.exec import run, run_or_fail
from mk.tools import Action, Tool


class NpmTool(Tool):
    name = "npm"

    def __init__(self, path=".") -> None:
        super().__init__(path=path)
        cmd = ["git", "ls-files", "**/package.json", "package.json"]
        result = run(cmd)
        if result.returncode != 0 or not result.stdout:
            self.present = False
            return
        self._actions: List[Action] = []
        for line in result.stdout.split():
            # we consider only up to one level deep files
            if line.count("/") > 1:
                continue
            cwd = line.split("/")[0]
            with open(line, "r") as package_json:
                data = json.load(package_json)
                if "scripts" in data:
                    for k in data["scripts"].keys():
                        self._actions.append(
                            Action(
                                name=k,
                                tool=self,
                                # description=cp[section]["description"],
                                args=[k],
                                cwd=cwd,
                            )
                        )
        self.present = bool(self._actions)

    def is_present(self, path: str) -> bool:
        return self.present

    def actions(self) -> List[Action]:
        return self._actions

    def run(self, action: Action = None) -> None:
        if not action:
            cmd = ["npm", "run"]
            cwd = None
        else:
            cmd = ["npm", "run", action.name]
            cwd = action.cwd
        run_or_fail(cmd, cwd=cwd, tee=True)
