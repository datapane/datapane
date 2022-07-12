export const codeMirror = () => {
    const cmEl: any = document.getElementsByClassName("CodeMirror")[0];
    return (cmEl as any).CodeMirror;
};

export const updateEditorAtCursor = (val: string): void => {
    try {
        const cm = codeMirror();
        let cursor = cm.getCursor();
        const cursorCh = cursor.ch;
        const token = cm.getTokenAt(cursor);
        const { line } = cursor;

        // Note - this is `token.state` when not using a custom language mode like xml-dp
        const { indented } = token.state.outer;

        val = val
            .replace(/\n(?!;)/g, `\n${Array(indented + 1).join(" ")}`)
            .replace(/;/g, "");

        setTimeout(() => {
            const doc: any = cm.getDoc();
            doc.replaceSelection(val);
            cm.focus();
            cursor = cm.getCursor();
            doc.setCursor({
                line,
                ch: cursorCh + val.length,
            });
        }, 0);
    } catch (e) {
        console.error("An error occurred while fetching CodeMirror", e);
    }
};

export const overwriteEditor = (val: string): void => {
    /**
     * After the initial load, editor state should be set inside codemirror using this function instead of directly
     * setting `store.editorContent`. This allows ctrl+z to undo the state set, and keeps the direction of data consistent
     */
    try {
        const cm = codeMirror();
        setTimeout(() => {
            cm.setValue(val);
        }, 0);
    } catch (e) {
        console.error("An error occurred while fetching CodeMirror", e);
    }
};
