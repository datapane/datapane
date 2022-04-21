export type ReportProps = {
    isOrg: boolean;
    mode: "VIEW" | "EMBED";
    disableTrackViews?: boolean;
    htmlHeader?: string;
    report: any; // TODO - type report
};
