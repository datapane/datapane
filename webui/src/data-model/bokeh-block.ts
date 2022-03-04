import { AssetBlock, Elem } from "./blocks";
import VBokehBlock from "../components/BokehBlock.connector.vue";
import { markRaw } from "vue";

export class BokehBlock extends AssetBlock {
  public component = markRaw(VBokehBlock);
  public componentProps: any;

  public constructor(elem: Elem) {
    super(elem);
    this.componentProps = { fetchAssetData: this.fetchRemoteAssetData };
  }
}
