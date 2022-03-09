import { markRaw } from "vue";
import { AssetBlock, Elem } from "../blocks";
import VDataTableBlock from "../../components/blocks/DataTable/DataTable.connector.vue";
import axios, { AxiosRequestConfig, AxiosResponse } from "axios";

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

  public get cells(): number {
    return this.rows * this.columns;
  }

  public get deferLoad(): boolean {
    return this.cells > AUTO_LOAD_CELLS_LIMIT;
  }

  public constructor(elem: Elem) {
    super(elem);
    const { attributes } = elem;
    this.rows = attributes.rows;
    this.columns = attributes.columns;
    this.size = attributes.size;
    this.casRef = attributes.cas_ref;
    this.componentProps = {
      streamContents: this.streamContents,
      deferLoad: this.deferLoad,
      cells: this.cells,
    };
  }

  private fetchDataset(opts: AxiosRequestConfig): Promise<any> {
    return axios.get(this.src, opts).then((r: AxiosResponse) => {
      return r.data;
    });
  }

  public streamContents = async (): Promise<DatasetResponse> => {
    const opts: AxiosRequestConfig = {
      responseType: "arraybuffer",
    };
    const { apiResponseToArrow } = await import("./arrow-utils");
    const arrayBuffer = await this.fetchDataset(opts);
    return await apiResponseToArrow(arrayBuffer);
  };
}
