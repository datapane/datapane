import * as React from "react";
import { useContext } from "react";
import { BuilderProviderContext } from "../../data-model/BuilderStore";
import { MobXProviderContext, observer } from "mobx-react";
import { Controlled as CodeMirror } from "react-codemirror2";
import CM from "codemirror";
import * as utls from "./utils";

import "codemirror/addon/display/placeholder";
import "codemirror/addon/fold/foldgutter";
import "codemirror/addon/fold/xml-fold";
import "codemirror/addon/hint/show-hint";
import "codemirror/addon/hint/xml-hint";
import "codemirror/mode/xml/xml";
import "codemirror/addon/mode/multiplex";
import "codemirror/addon/mode/overlay";
import "codemirror/addon/edit/closetag";

import "codemirror/theme/material.css";

export const Editor = observer(() => {
    const { store } = useContext<BuilderProviderContext>(MobXProviderContext);

    const onEditorChange = (val: string) => {
        store.editorContent = val;

        /* Unset on save */
        if (!window.onbeforeunload) {
            window.onbeforeunload = function () {
                return true;
            };
        }
    };

    return (
        <CodeMirror
            // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
            value={store.editorContent!}
            onBeforeChange={(editor, data, value) => onEditorChange(value)}
            options={{
                smartIndent: true,
                theme: "material",
                mode: "xml-dp",
                gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
                indentWithTabs: false,
                viewportMargin: Infinity,
                tabSize: 2,
                indentUnit: 2,
                extraKeys: {
                    Tab: utls.tabsToSpaces,
                    "Ctrl-Q": function (cm) {
                        cm.foldCode(cm.getCursor());
                    },
                    "'<'": utls.completeAfter as any, // React-codemirror typing issue
                    "'/'": utls.completeIfAfterLt,
                    "' '": utls.completeIfInTag,
                    "'='": utls.completeIfInTag,
                    "Ctrl-Space": "autocomplete",
                    "Shift-Tab": "indentLess",
                },
                hintOptions: { schemaInfo: utls.tags },
                lineWrapping: true,
                foldGutter: true,
                autoCloseTags: true,
            }}
            defineMode={
                {
                    name: "xml-dp",
                    fn: (config: any) => {
                        return CM.multiplexingMode(CM.getMode(config, "xml"), {
                            open: "[[",
                            close: "]]",
                            mode: CM.getMode(config, "text"),
                        });
                    },
                } as any
            }
        />
    );
});
