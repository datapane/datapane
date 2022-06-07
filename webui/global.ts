declare global {
    interface Window {
        dpLocal: boolean;
        reportProps?: any;
        posthog: any;
        hasPosthog: any;
        dpAuthorId: string;
        dpReportId: string;
        dpLocalViewEvent: any;
        Alpine: any;
        $testResources: any;
    }
}

export {};
