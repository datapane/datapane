import * as React from "react";
import { useContext, useEffect, useLayoutEffect, useState } from "react";
import { IReport } from "../../../legacy-report/utils";
import { Editor } from "./editor/Editor";
import { MobXProviderContext, observer, Provider } from "mobx-react";
import {
    BuilderProviderContext,
    builderStore,
} from "../data-model/BuilderStore";
import { DPButton } from "../../../legacy-report/DPButton";
import { NewBlocksIcons } from "./NewBlocksIcons";
import { ErrorPanel } from "./ErrorPanel";
import { PythonAssetsModal } from "./PythonAssetsModal";
import SplitPane from "react-split-pane";
import format from "xml-formatter";
import { overwriteEditor } from "../utils";
import { RefreshAssetsButton } from "./shared";
import {
    ClipboardCheckIcon,
    TerminalIcon,
    ArrowCircleLeftIcon,
} from "@heroicons/react/outline";

type Props = {
    initialReport: IReport;
    initialEditableDocument: string;
    isOrg: boolean;
    mountReport: (props: any) => any;
};

const ResizerStyle = {
    background: "#eee",
    width: "5px",
    cursor: "col-resize",
    height: "100%",
};

const BuilderContent = observer((p: Props) => {
    const [vueApp, setVueApp] = useState<any>();
    const { store } = useContext<BuilderProviderContext>(MobXProviderContext);

    const saveReport = () => {
        store.save();
    };

    const formatDocument = () => {
        const formatted = format(store.editorContent || "", {
            indentation: "  ",
            collapseContent: true,
        });
        overwriteEditor(formatted);
    };

    useEffect(() => {
        store.load(p.initialReport, p.initialEditableDocument);
    }, [p.initialReport, p.initialEditableDocument]);

    useLayoutEffect(() => {
        if (store.report && !store.errorMsg) {
            if (vueApp) {
                vueApp.unmount();
            }
            const app = p.mountReport({
                mode: "VIEW",
                report: store.report,
                isOrg: p.isOrg,
                disableTrackViews: true,
            });
            setVueApp(app);
        }
    }, [store.report, store.errorMsg]);

    const [modalIsOpen, setModalState] = useState(false);
    return (
        <div className="w-full flex flex-col">
            <PythonAssetsModal
                isOpen={modalIsOpen}
                close={() => setModalState(false)}
                insertAsset={() => {}}
            />
            <div
                className={
                    "h-12 px-4 bg-gray-100 border border-gray-300 block md:flex items-center justify-start p-4"
                }
            >
                <div className={"flex items-center space-x-2"}>
                    <NewBlocksIcons />
                    <DPButton
                        onClick={() => setModalState(true)}
                        className={" mr-2 border-gray-300 border"}
                        intent={"info"}
                        dataCy={"button-insert-assets"}
                    >
                        <TerminalIcon className={"h-5 w-5 mr-2"} />
                        Insert Python Assets
                    </DPButton>
                </div>
                <div className={"ml-auto flex items-center"}>
                    <a
                        href={p.initialReport.web_url}
                        className={
                            "dp-btn-sm dp-btn-info border border-gray-300 mr-2"
                        }
                    >
                        <ArrowCircleLeftIcon className={"mr-2 h-5 w-5"} /> Back
                        to report
                    </a>
                    <RefreshAssetsButton tipId={"main-component"} />
                    <DPButton
                        onClick={saveReport}
                        icon={"fa-floppy-o fa-lg"}
                        disabled={store.saving || !store.editorContent}
                        className={"shadow mr-2"}
                        intent={"primary"}
                    >
                        <span data-cy="button-save-changes">Save</span>
                    </DPButton>
                </div>
            </div>
            <div className={"h-full bg-white w-full"}>
                <SplitPane
                    className={"w-full h-auto"}
                    split={"vertical"}
                    defaultSize={"50%"}
                    resizerStyle={ResizerStyle}
                    onDragFinished={() =>
                        window.dispatchEvent(new Event("resize"))
                    }
                >
                    <div className={"h-full web-editor relative"}>
                        <div className={"absolute top-2 right-5 z-10"}>
                            <a
                                onClick={formatDocument}
                                className={
                                    "text-xs cursor-pointer p-2 text-gray-100 opacity-50 hover:opacity-100 flex items-center outline-none"
                                }
                            >
                                <ClipboardCheckIcon
                                    className={"w-5 h-5 mr-1"}
                                />
                                Reformat
                            </a>
                        </div>
                        <Editor />
                    </div>
                    <div
                        className={
                            "bg-white h-full flex-auto border border-t-0 border-l-0 border-gray-300 overflow-y-auto"
                        }
                    >
                        {store.report && !store.errorMsg ? (
                            <div id={"report"} />
                        ) : (
                            store.errorMsg && (
                                <ErrorPanel
                                    msg={store.errorMsg}
                                    className={"m-4"}
                                />
                            )
                        )}
                    </div>
                </SplitPane>
            </div>
        </div>
    );
});

export const BuilderComponent = (p: Props) => {
    /**
     * Top-level
     */
    return (
        <Provider store={builderStore}>
            <BuilderContent
                initialReport={p.initialReport}
                initialEditableDocument={p.initialEditableDocument}
                isOrg={p.isOrg}
                mountReport={p.mountReport}
            />
        </Provider>
    );
};
