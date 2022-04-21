import { markRaw } from "vue";
import { AssetBlock, Elem, ExportType } from "../blocks";
import VDataTableBlock from "../../components/blocks/DataTable/DataTable.connector.vue";
import axios, { AxiosRequestConfig, AxiosResponse } from "axios";
import download from "downloadjs";
import urljoin from "url-join";
import env from "../../environment";

const addQueryParam = (url: string, qp: { k: string; v: string }): string => {
    /**
     * Adds a query param k=v to a relative URL
     */
    const urlObj = new URL(url, env.url);
    const searchParams = urlObj.searchParams;
    searchParams.append(qp.k, qp.v);
    urlObj.search = searchParams.toString();
    return `${urlObj.pathname}?${urlObj.searchParams.toString()}`;
};

const filenameFromResponse = (response: Response): string => {
    /**
     * Creates a filename from file response header
     */
    const FALLBACK_NAME = "dp-export.csv";
    // eslint-disable-next-line
    const FILENAME_ATTR = 'filename="';
    const contentDisposition = response.headers.get("Content-Disposition");

    if (!contentDisposition || !contentDisposition.includes(FILENAME_ATTR)) {
        return FALLBACK_NAME;
    }

    // We use string split to extract the filename from header as FF doesn't support positive lookahead regexp
    // eslint-disable-next-line
    return contentDisposition.split(FILENAME_ATTR)[1].split('"')[0];
};

const downloadObject = async (url: string, mimeType: string) => {
    /**
     * Downloads a file from the server to the local client
     */
    try {
        const response = await fetch(urljoin(window.location.origin, url));
        if (response) {
            const blob = await response.blob();
            const filename = filenameFromResponse(response);
            download(blob, filename, mimeType);
        } else {
            console.error("No url provided");
        }
    } catch (e) {
        console.error(`An error occurred while downloading the file: ${e}`);
    }
};

const AUTO_LOAD_CELLS_LIMIT = 500000;

export type DatasetResponse = {
    data: any[];
    schema: any[];
    containsBigInt: boolean;
};

export class DataTableBlock extends AssetBlock {
    public component = markRaw(VDataTableBlock);
    public captionType = "Table";
    public componentProps: any;
    public rows: number;
    public columns: number;
    public size: number;
    public casRef: string;

    private webUrl: string;
    private _revogridExportPlugin: any;

    public get cells(): number {
        return this.rows * this.columns;
    }

    public get deferLoad(): boolean {
        return this.cells > AUTO_LOAD_CELLS_LIMIT;
    }

    public get exportUrl(): string {
        return this.buildExtensionUrl("export");
    }

    public constructor(
        elem: Elem,
        caption?: string,
        count?: number,
        opts?: any
    ) {
        super(elem, caption, count);
        const { attributes } = elem;
        this.rows = attributes.rows;
        this.columns = attributes.columns;
        this.size = attributes.size;
        this.casRef = attributes.cas_ref;
        this.webUrl = opts.webUrl;

        this.componentProps = {
            streamContents: this.streamContents,
            getCsvText: this.getCsvText,
            downloadLocal: this.downloadLocal,
            downloadRemote: this.downloadRemote,
            deferLoad: this.deferLoad,
            cells: this.cells,
            refId: this.refId,
        };
    }

    private fetchDataset(opts: AxiosRequestConfig): Promise<any> {
        return axios.get(this.src, opts).then((r: AxiosResponse) => {
            return r.data;
        });
    }

    public streamContents = async (): Promise<DatasetResponse> => {
        /**
         * Fetch dataset and convert to arrow format
         */
        const opts: AxiosRequestConfig = {
            responseType: "arraybuffer",
        };
        const { apiResponseToArrow } = await import("./arrow-utils");
        const arrayBuffer = await this.fetchDataset(opts);
        return apiResponseToArrow(arrayBuffer);
    };

    public downloadLocal = async (): Promise<void> => {
        /**
         * Download the current state of the DataTable via the client
         */
        try {
            const exportPlugin = await this.getExportPlugin();
            exportPlugin.exportFile({
                filename: `dp-export-${this.refId}`,
            });
        } catch (e) {
            console.error("An error occurred while exporting dataset: ", e);
        }
    };

    public downloadRemote = async (format: ExportType): Promise<void> => {
        /**
         * Download the original resource via the server
         */
        const exportUrl = addQueryParam(this.exportUrl, {
            k: "export_format",
            v: format,
        });
        const mimeType =
            format === "CSV"
                ? "text/csv"
                : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
        await downloadObject(exportUrl, mimeType);
    };

    public getCsvText = async (): Promise<string> => {
        /**
         * Return dataset contents as CSV string
         */
        let csvText = "";
        try {
            const exportPlugin = await this.getExportPlugin();
            csvText = exportPlugin.exportString();
        } catch (e) {
            console.error(
                "An error occurred while copying text to clipboard: ",
                e
            );
        }
        return csvText;
    };

    private async getExportPlugin(): Promise<any> {
        /**
         * Get revogrid export plugin from its HTML element root
         */
        if (this._revogridExportPlugin) {
            return this._revogridExportPlugin;
        }

        const grid = document.getElementById(
            `grid-${this.refId}`
        ) as HTMLRevoGridElement;

        if (grid) {
            const plugins = await grid.getPlugins();
            for (let p of plugins) {
                // Find export plugin by checking relevant properties
                if ((p as any).exportFile && (p as any).exportString) {
                    this._revogridExportPlugin = p;
                    return this._revogridExportPlugin;
                }
            }
        } else {
            throw "Grid element not found";
        }
    }

    private buildExtensionUrl(name: string): string {
        return new URL(
            `extensions/${name}/${this.casRef}`,
            this.webUrl
        ).toString();
    }
}
