from FeiQ.View.View import View, ViewType


class ContentView(View):
    def __init__(self, content):
        self.content = content
        View.__init__(self)

    def type(self):
        return ViewType.VIEW_CONTENT
