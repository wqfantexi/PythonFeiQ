from FeiQ.View.View import View, ViewType


class UserView(View):
    def __init__(self, user):
        self.user = user
        View.__init__(self)

    def type(self):
        return ViewType.VIEW_USER
