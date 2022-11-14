import {
    action,
    observable,
    reaction,
    makeObservable,
    transaction,
} from "mobx";
import { NStackApiInstance } from "../../../legacy-report/NStackApi";
import {
    IReport,
    IReportDocuments,
    isReportDocuments,
} from "../../../legacy-report/utils";
import { debounce } from "debounce";
import { extractAssets, NamedBlock } from "../metadata";
import { overwriteEditor } from "../utils";

const domParser = new DOMParser();

const DEBOUNCE_MS = 2000;

const validateXml = (xml: string) => {
    const dom = domParser.parseFromString(xml, "text/xml");
    const errorNodes = dom.getElementsByTagName("parsererror");
    if (errorNodes.length) {
        let errorMsg: string;
        try {
            // Only display the first XML error we come across
            const errorNode = errorNodes[0] as HTMLElement;
            errorMsg = errorNode.innerText.split("errors:")[1].split("\n")[0];
        } catch {
            // In case hacking the message out of the error node doesn't work
            errorMsg = "XML Parse error";
        }
        throw errorMsg;
    }
};

const bracesToCdata = (xml: string): string => {
    return xml.replace(/\[\[/g, "<![CDATA[").replace(/\]\]/g, "]]>");
};
const cDataToBraces = (xml: string): string => {
    return xml.replace(/<!\[CDATA\[/g, "[[").replace(/]]>/g, "]]");
};

enum UpdateAction {
    SAVE = "save",
    PREVIEW = "preview",
}

export class BuilderStore {
    public report?: IReport;
    public editorContent?: string;
    public saving = false;
    public errorMsg: string | null = null;
    public refreshingAssets = false;
    public showAssets = true;
    public unsavedChanges = false;
    public assets: NamedBlock[] = [];

    public constructor() {
        makeObservable(this, {
            assets: observable,
            unsavedChanges: observable,
            showAssets: observable,
            refreshingAssets: observable,
            errorMsg: observable,
            editorContent: observable,
            report: observable,
            saving: observable,
            load: action,
            save: action,
            preview: action,
            refreshAssets: action,
            onError: action,
            setReport: action,
        });
    }

    public async load(initialReport: IReport, initialEditableDocument: string) {
        try {
            transaction(() => {
                this.report = initialReport;
                // TODO(xml): what should the initial empty document be?
                this.editorContent = cDataToBraces(
                    initialEditableDocument || "",
                );
                this.refreshAssets();
            });
            this.initPreviewReaction();
        } catch (e) {
            this.onError(e);
        }
    }

    public save = async (): Promise<void> => {
        await this.setReport(UpdateAction.SAVE);
        if (!this.errorMsg) {
            this.unsavedChanges = false;
            /* Unbind the warning set on the CodeMirror component */
            window.onbeforeunload = null;
        }
    };

    public preview = debounce(async (): Promise<void> => {
        await this.setReport(UpdateAction.PREVIEW);
    }, DEBOUNCE_MS);

    public refreshAssets = async (
        opts: { remote: boolean } = { remote: false },
    ): Promise<any> => {
        /**
         * Refreshes the report from the BE or uses the provided report,
         * and sets assets from its `report_files` property
         */
        if (!this.report) throw "report not set";
        this.refreshingAssets = true;

        try {
            const reportToExtract = opts.remote
                ? await this.getRemoteReport()
                : this.report;
            this.assets = extractAssets(reportToExtract.report_files);
            if (opts.remote && isReportDocuments(reportToExtract)) {
                const newEditorContent = cDataToBraces(
                    reportToExtract.editable_document,
                );
                overwriteEditor(newEditorContent);
            }
        } catch (e) {
            this.errorMsg = "Couldn't fetch remote report";
            console.error(e);
        } finally {
            this.refreshingAssets = false;
        }
    };

    public onError(e: any) {
        console.error(e);
        if (e.response && e.response.data && e.response.data.non_field_errors) {
            this.errorMsg = e.response.data.non_field_errors[0];
        } else if (e.message) {
            this.errorMsg = e.message;
        } else {
            this.errorMsg = e;
        }
    }

    public async setReport(action: UpdateAction): Promise<void> {
        this.saving = true;
        try {
            const newReport: IReport = await this.postUpdatedRemoteReport(
                action,
            );
            this.report = newReport;
            if (action === UpdateAction.SAVE) {
                this.refreshAssets();
            }
            this.errorMsg = null;
        } catch (e) {
            this.onError(e);
        } finally {
            this.saving = false;
        }
    }

    private getRemoteReport(id?: string): Promise<IReportDocuments> {
        if (!this.report) throw "report not set";
        if (!id) {
            id = this.report.id;
        }
        return NStackApiInstance.get(`reports/${id}/report-editor/`);
    }

    private postUpdatedRemoteReport(action: UpdateAction): Promise<IReport> {
        /**
         * Post new report for save/preview
         */
        if (!this.report) throw "Report object not set";
        const transformedContent = bracesToCdata(this.editorContent || "");
        validateXml(transformedContent);
        return NStackApiInstance.post(
            `reports/${this.report.id}/report-editor/`,
            {
                editable_document: transformedContent,
                perform_save: action === UpdateAction.SAVE,
            },
        );
    }

    private initPreviewReaction() {
        reaction(
            () => this.editorContent,
            () => {
                this.unsavedChanges = true;
                (this.editorContent || this.editorContent === "") &&
                    this.preview();
            },
        );
    }
}

export const builderStore = new BuilderStore();

export type BuilderProviderContext = Record<string, BuilderStore>;
