declare global {
    interface Window {
        isIPythonEmbed: boolean;
        dpLocal: boolean;
        reportProps?: any;
        posthog: any;
        hasPosthog: any;
        dpAppRunner: boolean;
        dpAuthorId: string;
        dpReportId: string;
        dpLocalViewEvent: any;
        Alpine: any;
        $testResources: any;
        errorHandler: any;
    }
}

export {};
