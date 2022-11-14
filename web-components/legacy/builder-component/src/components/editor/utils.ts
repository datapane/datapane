import CM from "codemirror";

export const tabsToSpaces = (cm: any) => {
    /*
     * Support space indenting
     * See https://github.com/codemirror/CodeMirror/issues/988#issuecomment-14921785
     */
    if (cm.somethingSelected()) {
        cm.indentSelection("add");
    } else {
        cm.replaceSelection(
            cm.getOption("indentWithTabs")
                ? "\t"
                : Array(cm.getOption("indentUnit") + 1).join(" "),
            "end",
            "+input",
        );
    }
};

/* Autocomplete utils
 * Adapted from Codemirror XML autocomplete demo:
 * https://github.com/codemirror/CodeMirror/blob/73a5c219afb76f4bb813cce794d29a7b6a1ad500/demo/xmlcomplete.html
 */

export const completeAfter = (cm: any, pred: any) => {
    if (!pred || pred())
        setTimeout(function () {
            if (!cm.state.completionActive)
                cm.showHint({ completeSingle: false });
        }, 100);
    return CM.Pass;
};

export const completeIfAfterLt = (cm: any) => {
    return completeAfter(cm, function () {
        const cur = cm.getCursor();
        return cm.getRange(CM.Pos(cur.line, cur.ch - 1), cur) == "<";
    });
};

export const completeIfInTag = (cm: any) => {
    return completeAfter(cm, function () {
        const tok = cm.getTokenAt(cm.getCursor());
        if (
            tok.type == "string" &&
            (!/['"]/.test(tok.string.charAt(tok.string.length - 1)) ||
                tok.string.length == 1)
        )
            return false;
        const inner = CM.innerMode(cm.getMode(), tok.state).state;
        return inner.tagName;
    });
};

/* Autocomplete schema */
/* TODO - Replace dummy vals */

const commonAttrs = {
    label: null,
    name: null,
};

const commonChildren = [
    "Group",
    "Select",
    "BigNumber",
    "Formula",
    "Code",
    "Embed",
    "Text",
    "Asset",
    "HTML",
];

export const tags = {
    Page: {
        attrs: commonAttrs,
        children: commonChildren,
    },
    Group: {
        attrs: {
            ...commonAttrs,
            rows: null,
            columns: null,
        },
        children: commonChildren,
    },
    Select: {
        attrs: {
            ...commonAttrs,
            type: ["dropdown", "tabs"],
        },
        children: commonChildren,
    },
    BigNumber: {
        attrs: {
            ...commonAttrs,
            heading: null,
            value: null,
            change: null,
            prev_value: null,
            is_positive_intent: ["true", "false"],
            is_upward_change: ["true", "false"],
        },
    },
    Formula: {
        attrs: commonAttrs,
    },
    Code: {
        attrs: {
            ...commonAttrs,
            language: ["python", "javascript"],
        },
    },
    Embed: {
        attrs: {
            url: null,
            title: null,
            provider_name: null,
        },
    },
    Text: {
        attrs: commonAttrs,
    },
    HTML: {
        attrs: commonAttrs,
    },
    /* Assets */
    DataTable: {
        attrs: commonAttrs,
    },
    Table: {
        attrs: commonAttrs,
    },
    File: {
        attrs: commonAttrs,
    },
    Media: {
        attrs: commonAttrs,
    },
    Attachment: {
        attrs: {
            ...commonAttrs,
            filename: null,
        },
    },
    Plot: {
        attrs: {
            ...commonAttrs,
            responsive: null,
            scale: null,
        },
    },
};
