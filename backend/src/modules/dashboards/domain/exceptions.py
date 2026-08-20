from src.core.exceptions import EntityNotFoundError


class DashboardNotFoundError(EntityNotFoundError):
    def __init__(self, dashboard_id: object) -> None:
        super().__init__("Dashboard", dashboard_id)


class WidgetNotFoundError(EntityNotFoundError):
    def __init__(self, widget_id: object) -> None:
        super().__init__("Widget", widget_id)
