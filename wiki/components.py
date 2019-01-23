class Topbar:
    class Action:
        def __init__(self, name: str, href: str):
            self.name = name
            self.href = href

    def __init__(self):
        self.actions = []

    def add_action(self, action: Action):
        assert action, 'Action required!'
        self.actions.append(action)

