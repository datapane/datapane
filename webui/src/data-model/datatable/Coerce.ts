import * as R from "ramda";
import { DataType } from "apache-arrow";

/*
This class handled converting some of the more complex Arrow types into something we
can display within the browser, e.g. dates and big-ints.

It is constructed with the table field types, and these are used to dynamically create a coerceRow
function - this function takes a row from the table, and returns a JS compatible representation of
it. By default the coerceRow function is intialised with a single operation via R.pick that just
returns all the field names from the object as it was given.

Within the class constructor we iterate over the field names, looking for complex types we need to
process, in these cases, we generate a new function that processes and modifies that individual
field in the row, passing it on and composing it with the existing coerceRow function via R.compose.

Eventually we end up with a dynamically-built coerceRow function composed together where each one
will match it's own field and process it, and drop through to the next composed function, passing
the modified row along to it, until it ends up at the Pick function that returns the (now) modified object.
*/
export class Coerce {
  private fieldNames: string[] = [];
  public coerceRow = (row: any) => R.pick(this.fieldNames, row);

  public constructor(schemaFields: any[]) {
    for (const field of schemaFields) {
      if (DataType.isTimestamp(field)) {
        this.composeTimestampField(field);
      } else if (DataType.isInt(field)) {
        this.composeIntField(field);
      } else if (DataType.isFloat(field)) {
        this.composeFloatField(field);
      }

      this.fieldNames.push(field.name);
    }
  }

  private composeIntField(field: any) {
    if (field.type.bitWidth >= 64) {
      this.coerceRow = R.compose((row) => row, this.coerceRow);
    }
  }

  private composeFloatField(field: any) {
    this.coerceRow = R.compose((row) => {
      const val = row[field.name];
      if (val) {
        row[field.name] = parseFloat(val.toPrecision(4));
      }
      return row;
    }, this.coerceRow);
  }

  private composeTimestampField(field: any) {
    if (
      // only handle UTC or local timetamps
      field.type.timezone === null ||
      field.type.timezone === "UTC"
    ) {
      // It seems that our version of the arrow library
      // coerceRows all timestamp to millisecond resolution with
      // a normal JS Number representation regardless of the
      // resolution set on the field type metadata.
      // This is unlike the examples seen on the web for handling
      // timestamps which presumably work with an earlier version.
      // Therefore we do not need to check the 'field.type.unit' property
      // against 'TimeUnit', we can simply always pass the value to
      // 'new Date()'...
      this.coerceRow = R.compose((row) => {
        const val = row[field.name];
        if (val) {
          row[field.name] = new Date(val).toISOString();
        }
        return row;
      }, this.coerceRow);
    }
  }
}
