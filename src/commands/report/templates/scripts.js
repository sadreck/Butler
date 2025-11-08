const ExportManager = {
    export_data: function(data, format, filename) {
        if (format === 'clipboard') {
            navigator.clipboard.writeText(data).then(() => { /* Nothing */ });
        } else if (format === 'download') {
            const blob = new Blob([data], { type: "text/csv" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    }
}

const ChoicesTemplateManager = {
    item: function (strToEl, escapeForTemplate, classNames, data, html) {
        let output = ChoicesTemplateManager.__generateItem(
            [
                String(classNames.item),
                String(data.highlighted ? classNames.highlightedState : classNames.itemSelectable)
            ].join(' '),
            String(data.id),
            String(escapeForTemplate(true, data.value)),
            String(escapeForTemplate(true, data.label)),
            html
        );
        return strToEl(output);
    },

    choice: function (strToEl, escapeForTemplate, classNames, itemSelectText, data, html) {
        let output = ChoicesTemplateManager.__generateChoice(
            [
                String(classNames.item),
                String(classNames.itemChoice),
                String(data.disabled ? classNames.itemDisabled : classNames.itemSelectable)
            ].join(' '),
            String(itemSelectText),
            String(data.id),
            String(escapeForTemplate(true, data.value)),
            String(escapeForTemplate(true, data.label)),
            html
        )
        return strToEl(output);
    },

    __generateItem: function (classes, id, value, label, html) {
        return `<div
                    class="${classes}"
                    data-item
                    role="option"
                    data-id="${id}"
                    data-value="${value}"
                    data-deletable
                >
                ${html}
                ${label}
                <button type="button" class="choices__button" aria-label="Remove item: ${label}" data-button="">Remove item</button>
                </div>`;
    },

    __generateChoice: function (classes, text, id, value, label, html) {
        return `<div
                    class="${classes}"
                    data-select-text="${text}"
                    data-choice
                    data-choice-selectable
                    data-id="${id}"
                    data-value="${value}"
                >
                ${html}
                ${label}
                </div>`
    },

    init_with_count: function (element, placeholder) {
        return new Choices(
                element,
                {
                    removeItemButton: true,
                    searchResultLimit: -1,
                    placeholderValue: placeholder,
                    allowHTML: true,
                    shouldSort: false,
                    callbackOnCreateTemplates: function (strToEl, escapeForTemplate) {
                        let classNames = this.config.classNames;
                        let itemSelectText = this.config.itemSelectText;
                        return {
                            item: function({ classNames }, data) {
                                return ChoicesTemplateManager.item(strToEl, escapeForTemplate, classNames, data, '');
                            },
                            choice: function ({ classNames }, data) {
                                return ChoicesTemplateManager.choice(strToEl, escapeForTemplate, classNames, itemSelectText, data, `<span class="badge text-bg-primary me-2" style="width: 40px;">${$(data.element).data('count')}</span>`);
                            }
                        }
                    }
                }
            );
    }
};
