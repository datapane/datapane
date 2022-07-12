import { MobXProviderContext, observer } from "mobx-react";
import * as React from "react";
import { useContext, useEffect } from "react";
import ReactTooltip, { Place } from "react-tooltip";
import { DPButton } from "../../../legacy-report/DPButton";
import { BuilderProviderContext } from "../data-model/BuilderStore";
import { CloudDownloadIcon } from "@heroicons/react/outline";

type Props = {
    tipId: string;
    tipPosition?: Place;
};

export const RefreshAssetsButton = observer((p: Props) => {
    const { store } = useContext<BuilderProviderContext>(MobXProviderContext);

    useEffect(() => {
        /* Needed for tooltips on dynamic content */
        ReactTooltip.rebuild();
    });

    return (
        <React.Fragment>
            {/*LA - Disabled temporarily until we have a better locking story*/}
            {/*<ReactTooltip place={p.tipPosition || "bottom"} id={p.tipId} />*/}
            <span
                data-tip={
                    store.unsavedChanges
                        ? "Save your changes before loading updated assets."
                        : null
                }
                data-for={p.tipId}
            >
                <DPButton
                    onClick={() => store.refreshAssets({ remote: true })}
                    className={"border-gray-300 border mr-2"}
                    intent={"info"}
                    // disabled={store.unsavedChanges}
                >
                    <CloudDownloadIcon className={"w-5 h-5 mr-2"} />
                    Load server changes
                </DPButton>
            </span>
        </React.Fragment>
    );
});
