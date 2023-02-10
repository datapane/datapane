export type IReport = {
    document: any;
    web_url: string;
    output_is_light_prose: boolean;
    output_style_header: string;
    num_blocks: number;
    username: string;
    published: boolean;
    id: string;
};

export type ReportProps = {
    isOrg: boolean;
    isLightProse: boolean;
    mode: "VIEW" | "EMBED";
    htmlHeader: string;
    report: IReport;
    assetStore: any;
};

export type AppDataResult = {
    view_xml: string;
    assets: any;
};

export type AppData = {
    data: {
        result?: AppDataResult;
        error?: { message: string; code: number };
    };
};

export type AppMetaData = {
    isLightProse: ReportProps["isLightProse"];
    isOrg: ReportProps["isOrg"];
    mode: ReportProps["mode"];
    webUrl: string;
};

export enum SwapType {
    REPLACE = "replace",
    INNER = "inner",
    APPEND = "append",
    PREPEND = "prepend",
}

export enum TriggerType {
    SUBMIT = "submit",
    SCHEDULE = "schedule",
}
