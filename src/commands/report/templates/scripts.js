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
    }
};
