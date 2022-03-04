import { markRaw } from "vue";
import { AssetBlock, Elem } from "./blocks";
import VDataTableBlock from "../components/DataTableBlock.connector.vue";

export class DataTableBlock extends AssetBlock {
  public component = markRaw(VDataTableBlock);
  public componentProps: any;

  public constructor(elem: Elem) {
    super(elem);
    this.componentProps = {};
  }
}
