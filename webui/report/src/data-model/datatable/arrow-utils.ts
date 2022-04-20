import { DataType, Precision, Type, Table } from "apache-arrow";
import { Coerce } from "./Coerce";
import { DatasetResponse } from "./datatable-block";

export type FormattedNsSchemaField = {
    name: string;
    type: string;
};

const dataTypeToString = (typ: any): string => {
    // As for the most part we don't actually use the type
    // we can just switch on the tag, rather than calling
    // the type guards predicates in if/else blocks.
    // (the type guards also have an issue with ts >= 3.4)
    switch (typ.typeId) {
        case Type.Null: {
            return "null";
        }
        case Type.Int: {
            return "integer";
        }
        case Type.Float: {
            if (typ.precision === Precision.DOUBLE) {
                return "double";
            }
            return "float";
        }
        case Type.Binary:
        case Type.FixedSizeBinary: {
            return "binary";
        }
        case Type.Utf8: {
            return "string";
        }
        case Type.Bool: {
            return "boolean";
        }
        case Type.Decimal: {
            return "decimal";
        }
        case Type.Date: {
            return "date";
        }
        case Type.Time: {
            return "time";
        }
        case Type.Timestamp: {
            return "timestamp";
        }
        case Type.Interval: {
            return "interval";
        }
        case Type.List:
        case Type.FixedSizeList: {
            const subtype = dataTypeToString(typ.children[0].type);
            return `[${subtype}]`;
        }
        case Type.Struct: {
            return "struct";
        }
        case Type.Union: {
            return typ.children
                .map((i: any) => dataTypeToString(i.type))
                .filter((i: any) => i !== "null")
                .join(" or ");
        }
        case Type.Map: {
            return "map";
        }
        case Type.Dictionary: {
            if (DataType.isUtf8(typ.valueType)) {
                return "category";
            } else {
                return dataTypeToString(typ.valueType);
            }
        }
        default: {
            return typ.toString();
        }
    }
};

const extractArrowSchema = (sch: any): FormattedNsSchemaField[] => {
    return sch.fields.map((fld: any) => ({
        name: fld.name,
        type: dataTypeToString(fld.type),
    }));
};

export const apiResponseToArrow = (r: any): DatasetResponse => {
    const d: any[] = [];
    const table: any = Table.from(r);
    const coerce = new Coerce(table.schema.fields);

    for (const row of table) {
        d.push(coerce.coerceRow(row));
    }

    return {
        schema: extractArrowSchema(table.schema),
        data: d,
        // For now we want to disable sanddance for datasets containing int64 columns
        containsBigInt: table.schema.fields.some(
            (f: any) => f.type.bitWidth && f.type.bitWidth >= 64
        ),
    };
};
