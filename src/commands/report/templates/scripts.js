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
