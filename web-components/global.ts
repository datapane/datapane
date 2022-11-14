declare global {
    interface Window {
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
