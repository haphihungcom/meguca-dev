from meguca import exceptions


class DispatchUpdaterError(exceptions.Meguca):
    pass


class DispatchRendererError(DispatchUpdaterError):
    pass


class BBParserError(DispatchRendererError):
    pass


class TemplateRendererError(DispatchRendererError):
    pass