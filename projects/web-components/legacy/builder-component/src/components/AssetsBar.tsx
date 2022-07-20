import * as React from "react";
import { useContext, useMemo, useState } from "react";
import { AssetItem } from "./AssetItem";
import { NamedBlock } from "../metadata";
import { updateEditorAtCursor } from "../utils";
import { MobXProviderContext, observer } from "mobx-react";
import { BuilderProviderContext } from "../data-model/BuilderStore";
import { tags } from "./editor/utils";
import { Light as SyntaxHighlighter } from "react-syntax-highlighter";
import atomOneLight from "react-syntax-highlighter/dist/esm/styles/hljs/atom-one-light";
import python from "react-syntax-highlighter/dist/esm/languages/hljs/python";
import { ExclamationIcon } from "@heroicons/react/solid";

SyntaxHighlighter.registerLanguage("python", python);

type Props = {
    className?: string;
    assets?: NamedBlock[];
    updateEditor: (value: string, callback?: any) => void;
    saving: boolean;
    closeModal: () => void;
    refreshing: boolean;
};

// conditional drop assets
const dropAssets = (_: NamedBlock) => true;

const getAllowedProps = (tagName: string): string[] =>
    Object.keys((tags as any)[tagName].attrs);

const AssetsContent = observer((p: Pick<Props, "assets" | "closeModal">) => {
    // const c = useContext<BuilderProviderContext>(MobXProviderContext);
    // const { report } = c.store;

    // TODO - type asset
    const addAsset = (asset: any): void => {
        const allowedProps = ["src", ...getAllowedProps(asset.tagName)];
        // TODO - use xml-js?
        updateEditorAtCursor(
            `<${asset.tagName} ${Object.entries(asset.props)
                .filter(([k, _]) => allowedProps.includes(k))
                .map(([k, v]) => `${k}="${v}"`)
                .join(" ")}/>`
        );
        p.closeModal();
    };

    const atomicAssets = useMemo(
        () => (p.assets ? p.assets.filter(dropAssets) : []),
        [p.assets]
    );

    return atomicAssets && atomicAssets.length ? (
        <React.Fragment>
            <ul
                role="list"
                className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 sm:gap-x-6 lg:grid-cols-4 xl:gap-x-8"
            >
                {atomicAssets.map((asset, idx) => (
                    <AssetItem
                        key={asset.name}
                        asset={asset}
                        onClick={() => addAsset(asset)}
                    />
                ))}
            </ul>
        </React.Fragment>
    ) : (
        <span>
            You haven't uploaded any assets from Python into your report yet.{" "}
        </span>
    );
});

const exampleCode = (
    id: string
) => `import datapane as dp  # Import datapane's Python library
import altair as alt
from vega_datasets import data

df = data.stocks()

plot = alt.Chart(df).mark_line().encode(
    x='date', y='price',color='symbol', strokeDash='symbol',
).interactive()

dp.Report.by_id("${id}").update_assets(
    my_data=dp.DataTable(df),  # This could be any pandas DataFrame
    my_plot=dp.Plot(plot)  # This can be any plot from Altair, Plotly, Seaborn, etc.
)`;

const UploadInstructions = (props: { reportId: string }) => {
    return (
        <div>
            <span className={"text-base text-gray-700"}>
                Datapane allows you to upload assets (such as DataFrames and
                plots) from Python and use them in your report. After saving
                your web report, upload assets as demonstrated below, and press
                "Load changes from server". Your report's id is{" "}
                <b>{props.reportId}</b>.{" "}
            </span>

            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mt-3">
                <div className="flex">
                    <div className="flex-shrink-0">
                        <ExclamationIcon
                            className="h-5 w-5 text-yellow-400"
                            aria-hidden="true"
                        />
                    </div>
                    <div className="ml-3">
                        <p className="text-sm text-yellow-700">
                            Always save your web report before reloading assets
                            from Python, or unsaved changed will be overwritten.
                        </p>
                    </div>
                </div>
            </div>
            <div className={"mt-5 border-gray-300 border"}>
                <SyntaxHighlighter
                    language={"python"}
                    style={atomOneLight}
                    customStyle={{ padding: "1em" }}
                >
                    {exampleCode(props.reportId)}
                </SyntaxHighlighter>
            </div>
        </div>
    );
};

function classNames(...classes: any[]) {
    return classes.filter(Boolean).join(" ");
}

export const AssetsBar = observer((p: Props) => {
    const tabs = ["Existing assets", "Upload from Python"];
    const c = useContext<BuilderProviderContext>(MobXProviderContext);
    const { report } = c.store;

    const [currentTab, changeTab] = useState(
        p.assets && p.assets.length > 0 ? tabs[0] : tabs[1]
    );

    return (
        <div>
            <div className="flex items-center justify-start border-b border-gray-200">
                <div className="sm:hidden">
                    <select
                        id="tabs"
                        onChange={(v) => changeTab(v.target.value)}
                        name="tabs"
                        className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                        defaultValue={tabs.find((tab) => tab)}
                    >
                        {tabs.map((tab) => (
                            <option key={tab}>{tab}</option>
                        ))}
                    </select>
                </div>
                <div className="hidden sm:block">
                    <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                        {tabs.map((tab) => (
                            <a
                                onClick={() => changeTab(tab)}
                                key={tab}
                                href={"#"}
                                className={classNames(
                                    currentTab === tab
                                        ? "border-indigo-500 text-indigo-600"
                                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300",
                                    "whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
                                )}
                            >
                                {tab}
                            </a>
                        ))}
                    </nav>
                </div>
            </div>
            <div className={"h-full pt-4"}>
                {currentTab === "Existing assets" ? (
                    !p.refreshing ? (
                        <AssetsContent
                            assets={p.assets}
                            closeModal={p.closeModal}
                        />
                    ) : (
                        <div
                            className={
                                "w-full h-full flex justify-center pt-20"
                            }
                        >
                            <div className={"loader-lg"} />
                        </div>
                    )
                ) : (
                    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                    <UploadInstructions reportId={report!.id} />
                )}
            </div>
        </div>
    );
});
