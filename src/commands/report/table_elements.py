class TableColumnOptions:
    _name: str = None
    _visible: bool = None
    _label: str = None
    _link: str | None = None
    _type: str = None
    _align: str = None
    _icon_true: str = None
    _icon_false: str = None
    _style_true: str = None
    _style_false: str = None
    _column_control: str = None
    _column_control_alias: str = None
    _value_mapping: dict = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def label(self) -> str:
        return self._label or self.name

    @label.setter
    def label(self, value: str):
        self._label = value

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        self._visible = value

    @property
    def link(self) -> str | None:
        return self._link

    @link.setter
    def link(self, value: str):
        self._link = value

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def align(self) -> str:
        return self._align or ''

    @align.setter
    def align(self, value: str):
        self._align = value

    @property
    def icon_true(self) -> str:
        return self._icon_true

    @icon_true.setter
    def icon_true(self, value: str):
        self._icon_true = value

    @property
    def icon_false(self) -> str:
        return self._icon_false

    @icon_false.setter
    def icon_false(self, value: str):
        self._icon_false = value

    @property
    def style_true(self) -> str:
        return self._style_true

    @style_true.setter
    def style_true(self, value: str):
        self._style_true = value

    @property
    def style_false(self) -> str:
        return self._style_false

    @style_false.setter
    def style_false(self, value: str):
        self._style_false = value

    @property
    def column_control(self) -> str:
        match self.column_control_alias:
            case 'list-no-search':
                return "['order', [{ extend: 'searchList', search: false }]]"
            case 'list':
                return "['order', [{ extend: 'searchList' }]]"
            case _:
                return self._column_control

    @column_control.setter
    def column_control(self, value: str):
        self._column_control = value

    @property
    def column_control_alias(self) -> str:
        return self._column_control_alias

    @column_control_alias.setter
    def column_control_alias(self, value: str):
        self._column_control_alias = value

    @property
    def value_mapping(self) -> dict:
        return self._value_mapping or {}

    @value_mapping.setter
    def value_mapping(self, value: dict):
        self._value_mapping = value

    def __init__(self, name: str):
        self.name = name
        self.visible = True
        self.type = 'text'
        self.value_mapping = {}

class TableColumn:
    _name: str = None
    _contents: str = None
    _type: str = None
    _url: str = None
    _align: str = None
    _icon: str = None
    _style: str = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    def __init__(self, name: str):
        self.name = name
        self.type = 'text'

    @property
    def contents(self) -> str:
        return self._contents

    @contents.setter
    def contents(self, value: str):
        self._contents = value

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str):
        self._url = value

    @property
    def align(self) -> str:
        return self._align or ''

    @align.setter
    def align(self, value: str):
        self._align = value

    @property
    def icon(self) -> str:
        return self._icon

    @icon.setter
    def icon(self, value: str):
        self._icon = value

    @property
    def style(self) -> str:
        return self._style

    @style.setter
    def style(self, value: str):
        self._style = value

class Table:
    columns: dict = None

    rows: list = None

    def __init__(self, options: dict):
        if not options:
            options = {}
        self.columns = self._load_columns(options)
        self.rows = []

    def _load_columns(self, options: dict) -> dict:
        all_columns = {}
        for name, column_options in options.items():
            column = TableColumnOptions(name)
            if isinstance(column_options, str):
                if column_options == 'hide':
                    column.visible = False
            else:
                column.label = column_options.get('label', name)
                column.link = column_options.get('link', None)
                column.type = column_options.get('type', 'text')
                column.align = column_options.get('align', '')
                column.icon_true = column_options.get('format', {}).get('icon_true', 'fa-solid fa-circle-check')
                column.icon_false = column_options.get('format', {}).get('icon_false', 'fa-solid fa-circle-xmark')
                column.style_true = column_options.get('format', {}).get('style_true', '')
                column.style_false = column_options.get('format', {}).get('style_false', '')
                column.column_control = column_options.get('filters', {}).get('column_control', '[]')
                column.column_control_alias = column_options.get('filters', {}).get('column_control_alias', '')
                column.value_mapping = column_options.get('value_mapping', {})
            all_columns[name] = column
        return all_columns

    def header(self) -> list:
        header = []
        i = 0
        if len(self.columns) > 0:
            for name, column in self.columns.items():
                if not column.visible:
                    continue
                header.append({
                    'text': column.label,
                    'column': name,
                    'index': i
                })
                i += 1
        else:
            first_row = self.rows[0] if len(self.rows) > 0 else []
            for column in first_row:
                header.append({
                    'text': column.name,
                    'column': column.name,
                    'index': i
                })
                i += 1
        return header

    def filters(self) -> dict:
        filters = {}
        for name, column in self.columns.items():
            if not column.visible:
                continue
            elif column.column_control == '[]':
                continue
            filters[name] = {
                'column_control': column.column_control,
            }
        return filters

    def has_filters(self) -> bool:
        return len(self.filters()) > 0

    def load_rows(self, raw_results: list):
        for raw_result in raw_results:
            row = []
            for raw_column, raw_value in raw_result.items():
                if raw_column in self.columns and self.columns[raw_column].visible is False:
                    continue

                column = TableColumn(raw_column)
                column.contents = self._map_value(raw_column, raw_value)

                if raw_column in self.columns:
                    column.align = self.columns[raw_column].align

                    if self.columns[raw_column].type == 'link':
                        column = self._format_link(column, raw_result, raw_column)
                    elif self.columns[raw_column].type == 'icon':
                        column = self._format_icon(column, raw_column, raw_value)

                row.append(column)
            self.rows.append(row)

    def _map_value(self, raw_column: str, raw_value: str) -> str:
        if raw_column in self.columns and len(self.columns[raw_column].value_mapping) > 0:
            if raw_value in self.columns[raw_column].value_mapping:
                return self.columns[raw_column].value_mapping[raw_value]
            elif '_' in self.columns[raw_column].value_mapping:
                return self.columns[raw_column].value_mapping['_']
        return raw_value

    def _format_link(self, column: TableColumn, raw_result: dict, raw_column: str) -> TableColumn:
        column.type = 'link'
        column.url = raw_result[self.columns[raw_column].link] if self.columns[raw_column].link in raw_result else self.columns[raw_column].link
        return column

    def _format_icon(self, column: TableColumn, raw_column: str, raw_value: str | None) -> TableColumn:
        column.type = 'icon'
        if raw_value:
            column.icon = self.columns[raw_column].icon_true
            column.style = self.columns[raw_column].style_true
            column.contents = 'yes'
        else:
            column.icon = self.columns[raw_column].icon_false
            column.style = self.columns[raw_column].style_false
            column.contents = 'no'
        return column
