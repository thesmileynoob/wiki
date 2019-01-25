class Link:
    def __init__(self, name: str, href: str):
        self.name = name
        self.href = href


class Bar:
    def __init__(self):
        self.links = []

    def add_link(self, link: Link):
        assert link, 'Link required!'
        self.links.append(link)


class Topbar(Bar):
    pass


class Sidebar(Bar):
    def __init__(self, defaults=True):
        super().__init__()

        if defaults:
            self.add_link(Link('Home', '/'))
            self.add_link(Link('Add Page', '/new'))
            # self.add_link(Link('Settings', '/settings'))
            self.add_link(Link('Generate Dummy Pages', '/generate'))
            self.add_link(Link('Create Backup', '/backup'))


class Context:
    """ Namespace for templates """

    def __init__(self):
        self.title: str = ''
        self.topbar: Topbar = Topbar()
        self.sidebar: Sidebar = Sidebar()
